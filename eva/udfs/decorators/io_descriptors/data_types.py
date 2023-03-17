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
from typing import List, Tuple, Type
import numpy as np
import torch

from eva.catalog.catalog_type import NdArrayType
from eva.catalog.catalog_type import ColumnType, Dimension, NdArrayType
from eva.catalog.models.udf_io_catalog import UdfIOCatalogEntry
from eva.udfs.decorators.io_descriptors.abstract_types import (
    IOArgument,
    IOColumnArgument,
)
from eva.utils.errors import UDFIODefinitionError


class NumpyArray(IOColumnArgument):
    """Descriptor data type for Numpy Array"""

    def __init__(
        self,
        name: str,
        is_nullable: bool = False,
        type: NdArrayType = None,
        dimensions: Tuple[int] = None,
    ) -> None:
        super().__init__(
            name=name,
            type=ColumnType.NDARRAY,
            is_nullable=is_nullable,
            array_type=type,
            array_dimensions=dimensions,
        )
        
    def check_array_and_convert_shape(self, input_object):
        try:
            return np.reshape(input_object, self.array_dimensions)

        except Exception as e:

            raise UDFIODefinitionError(
                "The input object cannot be reshaped to %s. Error is %s"
                % (self.array_dimensions, str(e))
            )
                
    def check_array_and_convert_type(self, input_object):
        
        if not isinstance(input_object, np.ndarray):
            if isinstance(input_object, list):
                input_object = np.asarray(input_object)
            elif isinstance(input_object, torch.Tensor):
                input_object = input_object.numpy()
            else:
                raise UDFIODefinitionError("Unknown data type. Only input types List and Tensor can be converted to Numpy array")
            
        if self.array_type == NdArrayType.INT8:
            return input_object.astype(np.int8)
        elif self.type == NdArrayType.INT16:
            return input_object.astype(np.int16)
        elif self.array_type == NdArrayType.INT32:
            return input_object.astype(np.int32)
        elif self.array_type == NdArrayType.INT64:
            return input_object.astype(np.int64)
        elif self.array_type == NdArrayType.FLOAT32:
            return input_object.astype(np.float32)
        elif self.array_type == NdArrayType.FLOAT64:
            return input_object.astype(np.float64)
        else:
            raise UDFIODefinitionError("Unknown array type.")
        
 
class PyTorchTensor(IOColumnArgument):
    """Descriptor data type for PyTorch Tensor"""

    def __init__(
        self,
        name: str,
        is_nullable: bool = False,
        type: NdArrayType = None,
        dimensions: Tuple[int] = None,
    ) -> None:
        super().__init__(
            name=name,
            type=ColumnType.NDARRAY,
            is_nullable=is_nullable,
            array_type=type,
            array_dimensions=dimensions,
        )
                    
    def check_array_and_convert_shape(self, input_object):
        try:
            return torch.reshape(input_object, self.array_dimensions)

        except Exception as e:
            raise UDFIODefinitionError(
                "The input object cannot be reshaped to %s. Error is %s"
                % (self.array_dimensions, str(e))
            )
            
    def check_array_and_convert_type(self, input_object):
        
        if not isinstance(input_object, torch.Tensor):
            if isinstance(input_object, list):
                input_object = torch.Tensor(input_object)
            elif isinstance(input_object, np.ndarray):
                input_object = torch.from_numpy(input_object)
            else:
                raise UDFIODefinitionError("Unknown data type. Only input types List and Tensor can be converted to Numpy array")
            
        if self.array_type == NdArrayType.INT8:
            return input_object.to(torch.int8)
        elif self.type == NdArrayType.INT16:
            return input_object.to(torch.int16)
        elif self.array_type == NdArrayType.INT32:
            return input_object.to(torch.int32)
        elif self.array_type == NdArrayType.INT64:
            return input_object.to(torch.int64)
        elif self.array_type == NdArrayType.FLOAT32:
            return input_object.to(torch.float32)
        elif self.array_type == NdArrayType.FLOAT64:
            return input_object.to(torch.float64)
        else:
            raise UDFIODefinitionError("Unknown array type.")
    


class PandasDataframe(IOArgument):
    """Descriptor data type for Pandas Dataframe"""

    def __init__(self, columns, column_types=[], column_shapes=[]) -> None:
        super().__init__()
        self.columns = columns
        self.column_types = column_types
        self.column_shapes = column_shapes

    def generate_catalog_entries(self, is_input=False) -> List[Type[UdfIOCatalogEntry]]:
        catalog_entries = []

        if not self.column_types:
            self.column_types = [NdArrayType.ANYTYPE] * len(self.columns)

        if not self.column_shapes:
            self.column_shapes = [Dimension.ANYDIM] * len(self.columns)

        # check that columns, column_types and column_shpes are of same length
        if len(self.columns) != len(self.column_types) or len(self.columns) != len(
            self.column_shapes
        ):
            raise UDFIODefinitionError(
                "columns, column_types and column_shapes should be of same length if specified. "
            )

        for column_name, column_type, column_shape in zip(
            self.columns, self.column_types, self.column_shapes
        ):
            catalog_entries.append(
                UdfIOCatalogEntry(
                    name=column_name,
                    type=ColumnType.NDARRAY,
                    is_nullable=False,
                    array_type=column_type,
                    array_dimensions=column_shape,
                    is_input=is_input,
                )
            )

        return catalog_entries
    
    def check_array_and_convert_shape(self, input_obj):
        pass
    
    def check_array_and_convert_type(self, input_obj, data_type):
        pass
    
    def validate_pandas_outputs(self, input_obj):
        pass
