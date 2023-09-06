import sys
from collections import UserList
from dataclasses import MISSING, asdict, astuple, dataclass, fields
from typing import ClassVar, Iterator, Tuple, Union

from .exceptions import (
    GitmojiDataError,
    GitmojiListAttributeError,
    GitmojiListIndexError,
)
from .typing import (
    _GitmojiDict,
    _GitmojiField,
    _GitmojiListIndex,
)

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


@dataclass
class Gitmoji:
    emoji: _GitmojiField
    entity: _GitmojiField
    code: _GitmojiField
    description: _GitmojiField
    name: _GitmojiField
    semver: _GitmojiField = None

    def __hash__(self) -> int:
        return hash(astuple(self))

    @classmethod
    def from_dict(cls, /, __dict: _GitmojiDict) -> Self:
        for _field in fields(cls):
            if _field.default != MISSING:
                continue
            if _field.name not in __dict:
                raise GitmojiDataError(
                    f"The data dict doesn't contain the required field {_field.name!r}."
                )
        gitmoji_data = {
            field_name: field_value
            for field_name, field_value in __dict.items()
            if field_name in cls.__dataclass_fields__
        }
        return cls(**gitmoji_data)

    def to_dict(self) -> _GitmojiDict:
        return asdict(self)


class GitmojiList(UserList[Gitmoji]):
    _index_fields: ClassVar[Tuple[str, ...]] = ("name",)

    def __getitem__(self, __index: _GitmojiListIndex) -> Union[Gitmoji, Self]:  # type: ignore[override]
        if isinstance(__index, str):
            for gitmoji in self.data:
                if __index in [
                    getattr(gitmoji, _index_field)
                    for _index_field in self.__class__._index_fields
                ]:
                    return gitmoji
            raise GitmojiListIndexError(
                f"Gitmoji with the "
                f"{'/'.join(_index_field for _index_field in self._index_fields)} "
                f"{__index!r} not found."
            )
        elif isinstance(__index, int):
            try:
                return self.data[__index]
            except IndexError as exc:
                raise GitmojiListIndexError(
                    f"f{self.__class__.__name__} index out out range."
                ) from exc
        return self.__class__(self.data[__index])

    def iter_field(self, __field_name: str, /) -> Iterator[_GitmojiField]:
        if __field_name not in Gitmoji.__dataclass_fields__:
            raise GitmojiListAttributeError(
                f"One must not iterate over a non-existing field {__field_name!r}."
            )
        return iter([getattr(gitmoji, __field_name) for gitmoji in self.data])

    def iter_fields(self, /, *field_names: str) -> Iterator[Tuple[_GitmojiField, ...]]:
        if field_names == ():
            field_names = tuple(Gitmoji.__dataclass_fields__.keys())
        return zip(*(self.iter_field(field_name) for field_name in field_names))
