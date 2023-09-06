import pytest

from gitmoji.core import get_gitmojis
from gitmoji.exceptions import GitmojiLoaderError


@pytest.fixture()
def api_loader(mocker):
    return mocker.patch("gitmoji.core.load_gitmojis_from_api")


@pytest.fixture()
def json_loader(mocker):
    return mocker.patch("gitmoji.core.load_gitmojis_from_json")


def test_get_gitmojis_returns_api_data_if_no_loader_error(api_loader, json_loader):
    get_gitmojis()

    assert api_loader.called
    assert not json_loader.called


def test_get_gitmojis_returns_json_data_if_loader_error(api_loader, json_loader):
    api_loader.side_effect = GitmojiLoaderError

    get_gitmojis()

    assert json_loader.called
