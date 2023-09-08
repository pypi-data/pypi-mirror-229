#!/usr/bin/env python
# coding: utf-8

from time import ctime
from pathlib import Path
from functools import cached_property
import hashlib

class File:
    def __init__(self, filepath: str)-> None:
        self.filepath=Path(str(filepath))

    def __str__(self) -> str:
        file_prop: dict = self.properties
        if self.exists():
            return (
                f'Name        : {self.name}'
                f'\nDirectory   : {self.parent}'
                '\nExists          : True'
                f'\nAccess Time     : {file_prop["Access Time"]}'
                f'\nModified Time   : {file_prop["Modified Time"]}'
                f'\nChange Time     : {file_prop["Change Time"]}'
                f'\nSize            : {file_prop["Size_B"]/1024:.2f} KB'
            )
        else:
            return (
                f'Name        : {self.name}'
                f'\nDirectory   : {self.parent}'
                '\nExists          : False'
            )

    @property
    def hash(self) -> str:
        if self.filepath.exists():
            with open(self.filepath, 'rb') as f:
                _data: bytes = f.read()
            return hashlib.md5(_data).hexdigest()
        else:
            raise Exception(f"{self.filepath} does not exist.")

            
    def __repr__(self) -> str:
        return f'File(filepath="{self.filepath}")'
    
    def __del__(self) -> bool:
        if self.filepath.exists():
            self.filepath.unlink()
            return True
        else:
            return False

    @cached_property
    def stat(self):
        if self.exists():
            return self.filepath.stat()
        else:
            return None
    
    @property
    def name(self) -> str:
        "Returns the filename from the current self.filepath"
        return self.filepath.name

    @property
    def parent(self) -> Path:
        "Returns the file directory from the current self.filepath"
        return self.filepath.absolute().parent
    
    @property
    def abspath(self) -> Path:
        "Returns absolute path of the current file"
        return self.filepath.absolute()
    
    def __abs__(self) -> Path:
        return self.filepath.absolute()

    def update_filename(self, new_filename:str, rename_file: bool = False) -> str:
        "Updates the filepath of the stored file"
        new_filepath = self.filepath.parent / new_filename
        if rename_file and self.exists():
            self.filepath.rename(new_filepath)
            self.filepath = new_filepath
        return self.name
    
    def is_file(self) -> bool:
        return self.filepath.is_file()

    def exists(self) -> bool:
        return self.filepath.is_file()
    
    @property
    def atime(self) -> float|None:
        return self.stat.st_atime if self.stat else None
    
    @property
    def ctime(self) -> float|None:
        return self.stat.st_ctime if self.stat else None
    
    @property
    def mtime(self) -> float|None:
        return self.stat.st_mtime if self.stat else None
    
    @property
    def properties(self) -> dict:
        "Returns a dict of properties of the file"
        stat = self.stat if self.exists() else None
        return {
            "name": self.name,
            "dir": self.parent,
            "exists": self.exists(),
            "Access Time": ctime(self.atime) if stat else None,
            "Modified Time": ctime(self.mtime) if stat else None,
            "Change Time" : ctime(self.ctime) if stat else None,
            "Size_B": stat.st_size if stat else None
        }
        
    def __len__(self) -> int:
        """Returns size of file in Bytes
        """
        if self.exists() and self.stat:
            return self.stat.st_size
        else:
            return 0
        
    def __gt__(self, other) -> bool:
        if isinstance(other, File):
            return len(self) > len(other)
        elif type(other) in (int, float):
            return len(self) > other
        else:
            raise TypeError(f"Unsupported comparison between instances of 'File' and '{other.__class__.__name__}'")  # noqa: E501

    def __lt__(self, other) -> bool:
        if isinstance(other, File):
            return len(self) < len(other)
        elif type(other) in (int, float):
            return len(self) < other
        else:
            raise TypeError(f"Unsupported comparison between instances of 'File' and '{other.__class__.__name__}'")  # noqa: E501

    def __ge__(self, other) -> bool:
        if isinstance(other, File):
            return len(self) >= len(other)
        elif type(other) in (int, float):
            return len(self) >= other
        else:
            raise TypeError(f"Unsupported comparison between instances of 'File' and '{other.__class__.__name__}'")  # noqa: E501

    def __le__(self, other) -> bool:
        if isinstance(other, File):
            return len(self) <= len(other)
        elif type(other) in (int, float):
            return len(self) <= other
        else:
            raise TypeError(f"Unsupported comparison between instances of 'File' and '{other.__class__.__name__}'")  # noqa: E501

    def __eq__(self, other) -> bool:
        if isinstance(other, File):
            return self.hash == other.hash
        elif isinstance(other, str):
            return self.hash == other
        elif isinstance(other, int):
            return len(self) == other
        else:
            raise TypeError(f"Unsupported comparison between instances of 'File' and '{other.__class__.__name__}'")  # noqa: E501
