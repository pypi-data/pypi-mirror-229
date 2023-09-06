class GitmojiException(Exception):
    """A base class for all custom exceptions used in the `gitmoji` package."""


class GitmojiError(GitmojiException):
    """Raised when the `gitmoji.model.Gitmoji` class displays an unexpected behavior."""


class GitmojiDataError(GitmojiError):
    """Raised when a `gitmoji.model.Gitmoji` object is created with invalid data."""


class GitmojiListError(GitmojiException):
    """Raised when the `gitmoji.model.GitmojiList` class displays an unexpected behavior."""


class GitmojiListIndexError(GitmojiException, IndexError):
    """Raised when a `gitmoji.model.GitmojiList` object is indexed with an invalid index."""


class GitmojiListAttributeError(GitmojiError, AttributeError):
    """Raised when a non-existing field of a `gitmoji.model.Gitmoji` object is referred to."""


class GitmojiLoaderError(GitmojiException):
    """Raised when objects of the `gitmoji.loaders.GitmojiBaseLoader` subclasses display unexpected behavior."""
