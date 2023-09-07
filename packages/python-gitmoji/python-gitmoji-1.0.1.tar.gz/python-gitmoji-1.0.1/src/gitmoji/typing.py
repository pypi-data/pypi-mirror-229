import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

# Related to `gitmoji.model.Gitmoji`

_GitmojiField: TypeAlias = Optional[str]

_GitmojiDict: TypeAlias = Dict[str, _GitmojiField]


# Related to `gitmoji.model.GitmojiList`

_GitmojiListIndex: TypeAlias = Union[int, slice, str]


# Related to `gitmoji.loaders.GitmojiBaseLoader` and subclasses

_GitmojiLoaderSrc: TypeAlias = Any

_GitmojiLoaderOutput: TypeAlias = List[_GitmojiDict]


# Related to `gitmoji.loaders.GitmojiApiLoader`

_GitmojiApiLoaderSrc: TypeAlias = str


# Related to `gitmoji.loaders.GitmojiJsonLoader`

_GitmojiJsonLoaderSrc: TypeAlias = Union[str, Path]
