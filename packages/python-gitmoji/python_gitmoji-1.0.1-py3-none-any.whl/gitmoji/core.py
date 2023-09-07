from .exceptions import GitmojiLoaderError
from .loaders import GitmojiApiLoader, GitmojiJsonLoader
from .model import GitmojiList

load_gitmojis_from_api = GitmojiApiLoader()

load_gitmojis_from_json = GitmojiJsonLoader()


def get_gitmojis() -> GitmojiList:
    try:
        gitmojis = load_gitmojis_from_api()
    except GitmojiLoaderError:
        gitmojis = load_gitmojis_from_json()
    return gitmojis


gitmojis = get_gitmojis()
