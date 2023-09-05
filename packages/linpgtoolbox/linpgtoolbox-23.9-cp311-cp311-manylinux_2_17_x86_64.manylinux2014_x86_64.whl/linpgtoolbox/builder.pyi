from ._execute import execute_python as execute_python
from .pkginstaller import PackageInstaller as PackageInstaller
from .pyinstaller import PyInstaller as PyInstaller
from _typeshed import Incomplete
from enum import IntEnum
from typing import Any

class SmartAutoModuleCombineMode(IntEnum):
    DISABLE: Incomplete
    FOLDER_ONLY: Incomplete
    ALL_INTO_ONE: Incomplete

class Builder:
    @staticmethod
    def remove(*path: str) -> None: ...
    @staticmethod
    def copy(files: tuple[str, ...], target_folder: str) -> None: ...
    @classmethod
    def compile(cls, source_folder: str, target_folder: str = ..., additional_files: tuple[str, ...] = ..., ignore_key_words: tuple[str, ...] = ..., smart_auto_module_combine: SmartAutoModuleCombineMode = ..., remove_building_cache: bool = ..., update_the_one_in_sitepackages: bool = ..., include_pyinstaller_program: bool = ..., options: dict[str, Any] = ...) -> None: ...
    @classmethod
    def build(cls) -> None: ...
    @classmethod
    def upload(cls, confirm: bool = ...) -> None: ...
