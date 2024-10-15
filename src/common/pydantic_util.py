from typing import TypeVar, Type, Union
import os
from pydantic import BaseModel

T = TypeVar('T', bound='BaseConfig')


class BaseConfig(BaseModel):
    @classmethod
    def from_file(cls: Type[T], file_path: Union[str, os.PathLike]) -> T:
        try:
            with open(file_path, 'r') as file:
                return cls.model_validate_json(file.read())
        except Exception as e:
            raise ValueError(f"Failed to read and parse configuration: {e}")

    def to_file(self, file_path: Union[str, os.PathLike]):
        try:
            with open(file_path, 'w') as file:
                file.write(self.model_dump_json(indent=4))
        except Exception as e:
            raise ValueError(f"Failed to store configuration: {e}")


