import json
from pathlib import Path
from typing import ClassVar, Optional

import requests
from requests import ConnectionError, HTTPError, RequestException

from .exceptions import GitmojiLoaderError
from .model import Gitmoji, GitmojiList
from .typing import (
    _GitmojiApiLoaderSrc,
    _GitmojiJsonLoaderSrc,
    _GitmojiLoaderOutput,
    _GitmojiLoaderSrc,
)


class GitmojiBaseLoader:
    def __init__(self, default_src: Optional[_GitmojiLoaderSrc] = None) -> None:
        self._default_src = default_src

    def __call__(self, src: Optional[_GitmojiLoaderSrc] = None) -> GitmojiList:
        if src is None and self._default_src is None:
            raise GitmojiLoaderError(
                f"Calling {self.__class__.__name__} objects whose default source is "
                f"unset requires specifying a data source."
            )
        _fetched_gitmoji_dicts = self._fetch(src)
        return GitmojiList(
            [
                Gitmoji.from_dict(_fetched_gitmoji_dict)
                for _fetched_gitmoji_dict in _fetched_gitmoji_dicts
            ]
        )

    def _fetch(self, src: _GitmojiLoaderSrc) -> _GitmojiLoaderOutput:
        raise NotImplementedError(
            f"Subclasses of {self.__class__.__base__.__name__} must implement the "
            f"'_fetch' method."
        )


class GitmojiApiLoader(GitmojiBaseLoader):
    DEFAULT_API_URL: ClassVar[str] = "https://gitmoji.dev/api/gitmojis"

    def __init__(self, default_src: Optional[_GitmojiApiLoaderSrc] = None) -> None:
        if default_src:
            raise self._get_api_error()
        super().__init__(self.__class__.DEFAULT_API_URL)

    def __call__(self, src: Optional[_GitmojiApiLoaderSrc] = None) -> GitmojiList:
        if src:
            raise self._get_api_error()
        return super().__call__(self._default_src)

    def _fetch(self, src: _GitmojiApiLoaderSrc) -> _GitmojiLoaderOutput:
        try:
            (response := requests.get(src)).raise_for_status()
            gitmojis = response.json()["gitmojis"]
        except (ConnectionError, HTTPError, RequestException) as exc_info:
            try:
                exc_message = f"HTTP status code = {response.status_code}"
            except UnboundLocalError:
                exc_message = "connection or request error"
            raise GitmojiLoaderError(
                f"Downloading data from the Gitmoji API endpoint '{src}' "
                f"failed due to {exc_message}."
            ) from exc_info
        return gitmojis  # type: ignore[no-any-return]  # json.load returns `Any`

    @classmethod
    def _get_api_error(cls) -> GitmojiLoaderError:
        return GitmojiLoaderError(
            f"{cls.__name__} doesn't support APIs other than {cls.DEFAULT_API_URL!r}."
        )


class GitmojiJsonLoader(GitmojiBaseLoader):
    DEFAULT_JSON_FILE_PATH: ClassVar[Path] = (
        Path(__file__).parent / "assets" / "gitmojis.json"
    )

    def __init__(self, default_src: Optional[_GitmojiJsonLoaderSrc] = None) -> None:
        super().__init__(default_src or self.__class__.DEFAULT_JSON_FILE_PATH)

    def __call__(self, src: Optional[_GitmojiJsonLoaderSrc] = None) -> GitmojiList:
        return super().__call__(src or self._default_src)

    def _fetch(self, src: _GitmojiJsonLoaderSrc) -> _GitmojiLoaderOutput:
        try:
            with Path(src).open(encoding="UTF-8") as fp:
                gitmojis = json.load(fp)["gitmojis"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc_info:
            exc_message = {
                FileNotFoundError: "the source doesn't exist",
                json.JSONDecodeError: "the source isn't a valid JSON file",
                KeyError: "the source's format is invalid",
            }.get(exc_info.__class__)
            raise GitmojiLoaderError(
                f"Loading data from JSON file {src} failed because {exc_message}."
            ) from exc_info
        return gitmojis  # type: ignore[no-any-return]  # json.load returns `Any`
