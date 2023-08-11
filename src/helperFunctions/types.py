from multiprocessing.sharedctypes import Synchronized, SynchronizedArray
from tempfile import _TemporaryFileWrapper
from typing import TypeVar, TypeAlias, NamedTuple

KT = TypeVar('KT', str, tuple, bytes)  # generic key type
VT = TypeVar('VT')  # generic value type

# NamedTemporaryFile is actually a function that returns an instance of class _TemporaryFileWrapper, so it can't be
# used for type hinting
TmpFile: TypeAlias = _TemporaryFileWrapper

# multiprocessing.Value returns "SynchronizedBase[Any]" which has no attribute "value". This is a known bug in
# mypy, see https://github.com/python/typeshed/issues/8799 -> ignore assignment and treat as Synchronized
MpValue: TypeAlias = Synchronized
MpArray: TypeAlias = SynchronizedArray


class AnalysisPluginInfo(NamedTuple):
    description: str
    mandatory: bool
    presets: dict
    version: str
    dependencies: list[str]
    blacklist: list[str]
    whitelist: list[str]
    worker_count: int
