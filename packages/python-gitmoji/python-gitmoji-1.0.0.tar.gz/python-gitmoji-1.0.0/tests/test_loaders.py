import json

import pytest
from requests import ConnectionError, HTTPError, RequestException

from gitmoji.exceptions import GitmojiLoaderError
from gitmoji.loaders import GitmojiApiLoader, GitmojiBaseLoader, GitmojiJsonLoader
from gitmoji.model import Gitmoji, GitmojiList


class _TestGitmojiLoaderMixin:
    @pytest.fixture()
    def gitmojis_json(self):
        return {
            "gitmojis": [
                {
                    "emoji": "🤡",
                    "entity": "&#129313;",
                    "code": ":clown_face:",
                    "description": "Mock things.",
                    "name": "clown-face",
                    "semver": None,
                }
            ]
        }

    @pytest.fixture(autouse=True)
    def _mock_gitmoji_list(self, gitmojis_json):
        self.gitmoji_list = GitmojiList(
            [
                Gitmoji.from_dict(gitmoji_dict)
                for gitmoji_dict in gitmojis_json["gitmojis"]
            ]
        )


class TestGitmojiBaseLoader(_TestGitmojiLoaderMixin):
    @pytest.fixture(autouse=True)
    def _mock_loader(self, gitmojis_json):
        class GitmojiMockLoader(GitmojiBaseLoader):
            def _fetch(self, src):
                return gitmojis_json["gitmojis"]

        self.loader = GitmojiMockLoader

    def test_loading_works_if_called_with_no_src_if_default_src(self):
        load_gitmojis = self.loader(default_src="default_src")

        gitmojis = load_gitmojis()

        assert isinstance(gitmojis, GitmojiList)
        assert load_gitmojis() == self.gitmoji_list

    def test_loading_fails_if_called_with_no_src_and_no_default_src(self):
        load_gitmojis = self.loader()

        with pytest.raises(GitmojiLoaderError):
            load_gitmojis()

    def test_loader_without_fetch_implemented_raises_error_when_called(self):
        class GitmojiLoader(GitmojiBaseLoader):
            pass

        load_gitmojis = GitmojiLoader(default_src="default_src")

        with pytest.raises(
            NotImplementedError,
            match="Subclasses of GitmojiBaseLoader must implement the '_fetch' method.",
        ):
            load_gitmojis()


class TestGitmojiApiLoader(_TestGitmojiLoaderMixin):
    @pytest.fixture(autouse=True)
    def _mock_requests_get(self, mocker, gitmojis_json):
        requests_get = mocker.patch("requests.get")
        requests_get.return_value.json.return_value = gitmojis_json

    def test_loading_works_if_called_with_official_api(self):
        load_gitmojis = GitmojiApiLoader()
        gitmojis = load_gitmojis()

        assert isinstance(gitmojis, GitmojiList)
        assert gitmojis == self.gitmoji_list

    def test_loading_fails_if_unofficial_api_called(self):
        load_gitmojis = GitmojiApiLoader()

        with pytest.raises(GitmojiLoaderError):
            load_gitmojis("https://gitmoji.dev/unofficial-api/gitmojis")

    def test_loading_fails_if_created_unofficial_api(self):
        with pytest.raises(GitmojiLoaderError):
            GitmojiApiLoader("https://gitmoji.dev/unofficial-api/gitmojis")

    @pytest.mark.parametrize(
        "requests_error",
        [
            ConnectionError,
            HTTPError,
            RequestException,
        ],
    )
    def test_loading_fails_if_called_with_requests_error(self, mocker, requests_error):
        mocker.patch("requests.get", side_effect=requests_error)

        load_gitmojis = GitmojiApiLoader()

        with pytest.raises(
            GitmojiLoaderError,
            match=r"Downloading data from the Gitmoji API endpoint .* failed",
        ) as exc_info:
            load_gitmojis()
        assert isinstance(exc_info.value.__cause__, requests_error)

    def test_loading_fails_if_connection_error(self, mocker):
        mocker.patch("requests.get", side_effect=ConnectionError)

        load_gitmojis = GitmojiApiLoader()

        with pytest.raises(
            GitmojiLoaderError, match="connection or request error"
        ) as exc_info:
            load_gitmojis()
        assert isinstance(exc_info.value.__cause__, ConnectionError)

    def test_loading_fails_if_http_response_error(self, mocker):
        requests_get = mocker.patch("requests.get")
        requests_get.return_value.status_code = 404
        requests_get.return_value.raise_for_status.side_effect = HTTPError

        load_gitmojis = GitmojiApiLoader()

        with pytest.raises(
            GitmojiLoaderError, match="HTTP status code = 404"
        ) as exc_info:
            load_gitmojis()
        assert isinstance(exc_info.value.__cause__, HTTPError)


class TestGitmojiJsonLoader(_TestGitmojiLoaderMixin):
    @pytest.fixture(autouse=True)
    def _mock_json_path(self, tmp_path):
        self.json_path = tmp_path / "gitmojis.json"

    def test_loading_works_with_default_json_file(self, mocker, gitmojis_json):
        mocker.patch(
            "gitmoji.loaders.GitmojiJsonLoader.DEFAULT_JSON_FILE_PATH",
            self.json_path,
        )
        with self.json_path.open("w", encoding="UTF-8") as fp:
            json.dump(gitmojis_json, fp, ensure_ascii=False)

        load_gitmojis = GitmojiJsonLoader()
        gitmojis = load_gitmojis()

        assert isinstance(gitmojis, GitmojiList)
        assert gitmojis == self.gitmoji_list

    def test_loading_works_with_custom_json_file(self, gitmojis_json):
        with self.json_path.open("w", encoding="UTF-8") as fp:
            json.dump(gitmojis_json, fp, ensure_ascii=False)

        load_gitmojis = GitmojiJsonLoader(self.json_path)
        gitmojis = load_gitmojis()

        assert isinstance(gitmojis, GitmojiList)
        assert gitmojis == self.gitmoji_list

    def test_loading_fails_with_non_existing_file(self, tmp_path):
        load_gitmojis = GitmojiJsonLoader()

        with pytest.raises(
            GitmojiLoaderError, match="the source doesn't exist"
        ) as exc_info:
            load_gitmojis(tmp_path / "does_not_exits.json")
        assert isinstance(exc_info.value.__cause__, FileNotFoundError)

    def test_loading_fails_with_invalid_json_file(self):
        with self.json_path.open("w", encoding="UTF-8") as fp:
            fp.write("// this is not a valid JSON")

        load_gitmojis = GitmojiJsonLoader()

        with pytest.raises(
            GitmojiLoaderError, match="the source isn't a valid JSON file"
        ) as exc_info:
            load_gitmojis(self.json_path)
        assert isinstance(exc_info.value.__cause__, json.JSONDecodeError)

    def test_loading_fails_with_invalid_data_format(self):
        with self.json_path.open("w", encoding="UTF-8") as fp:
            json.dump({"not-gitmojis": []}, fp, ensure_ascii=False)

        load_gitmojis = GitmojiJsonLoader()

        with pytest.raises(
            GitmojiLoaderError, match="the source's format is invalid"
        ) as exc_info:
            load_gitmojis(self.json_path)
        assert isinstance(exc_info.value.__cause__, KeyError)
