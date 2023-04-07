# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import List

from eva.udfs.decorators.io_descriptors.abstract_types import IOArgument
from eva.utils.errors import UDFIODefinitionError


def setup(cachable: bool = False, udf_type: str = "Abstract", batchable: bool = True):
    """decorator for the setup function. It will be used to set the cache, batching and
    udf_type parameters in the catalog

    Args:
        use_cache (bool): True if the udf should be cached
        udf_type (str): Type of the udf
        batch (bool): True if the udf should be batched
    """

    def inner_fn(arg_fn):
        def wrapper(*args, **kwargs):
            # calling the setup function defined by the user inside the udf implementation
            arg_fn(*args, **kwargs)

        tags = {}
        tags["cachable"] = cachable
        tags["udf_type"] = udf_type
        tags["batchable"] = batchable
        wrapper.tags = tags
        return wrapper

    return inner_fn


def forward(input_signatures: List[IOArgument], output_signatures: List[IOArgument], check_input: bool = True, check_output: bool = True):
    """decorator for the forward function. It will be used to set the input and output.

    Args:
        input_signature (List[IOArgument]): List of input arguments for the udf
        output_signature ( List[IOArgument])): List of output arguments for the udf
    """

    def inner_fn(arg_fn):
        def wrapper(*args):

            # checking the user constraints
            if check_input:
                if len(input_signatures) > 0:
                    args_lst = []
                    if len(args) > 0:
                        args_lst.append(args[0])

                    for i, input_signature in enumerate(input_signatures):
                        try:
                            args_lst.append(
                                # the first object in the forward function is self so we start from the second object
                                input_signature.validate_object(args[i + 1], True)
                            )
                        except UDFIODefinitionError as e:
                            raise UDFIODefinitionError(str(e))

                    if len(args_lst) > 0:
                        args = tuple(args_lst)

            # calling the forward function defined by the user inside the udf implementation
            output = arg_fn(*args)

            if check_output:
                if len(output_signatures) == 1:
                    try:
                        return output_signatures[0].validate_object(output, False)
                    except UDFIODefinitionError as e:
                        raise UDFIODefinitionError(str(e))
                else:
                    output_lst = []
                    for i, output_signature in enumerate(output_signatures):
                        try:
                            output_lst.append(output_signature.validate_object(output[i]))

                        except UDFIODefinitionError as e:
                            raise UDFIODefinitionError(str(e))

                    output = tuple(output)

            return output

        tags = {}
        tags["input"] = input_signatures
        tags["output"] = output_signatures
        wrapper.tags = tags
        return wrapper

    return inner_fn
