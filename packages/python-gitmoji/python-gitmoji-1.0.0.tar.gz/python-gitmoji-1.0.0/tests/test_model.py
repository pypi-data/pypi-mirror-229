from dataclasses import MISSING, astuple, fields

import pytest

from gitmoji.exceptions import (
    GitmojiDataError,
    GitmojiListAttributeError,
    GitmojiListIndexError,
)
from gitmoji.model import Gitmoji, GitmojiList


class TestGitmoji:
    @pytest.fixture(autouse=True)
    def _mock_gitmoji_fields_dict(self):
        self.gitmoji_dict = {
            "emoji": "🤡",
            "entity": "&#129313;",
            "code": ":clown_face:",
            "description": "Mock things.",
            "name": "clown-face",
            "semver": None,
        }

    def test_from_dict_works_if_all_fields(self):
        gitmoji = Gitmoji.from_dict(self.gitmoji_dict)

        assert isinstance(gitmoji, Gitmoji)

    @pytest.mark.parametrize(
        "optional_field",
        [field.name for field in fields(Gitmoji) if field.default != MISSING],
    )
    def test_from_dict_works_if_optional_field_missing(self, optional_field):
        self.gitmoji_dict.pop(optional_field)

        gitmoji = Gitmoji.from_dict(self.gitmoji_dict)

        assert optional_field not in self.gitmoji_dict
        assert isinstance(gitmoji, Gitmoji)

    @pytest.mark.parametrize(
        "required_field",
        [field.name for field in fields(Gitmoji) if field.default == MISSING],
    )
    def test_from_dict_fails_if_required_field_missing(self, required_field):
        self.gitmoji_dict.pop(required_field)

        with pytest.raises(GitmojiDataError):
            Gitmoji.from_dict(self.gitmoji_dict)
        assert required_field not in self.gitmoji_dict

    def test_to_dict(self):
        gitmoji = Gitmoji.from_dict(self.gitmoji_dict)

        assert gitmoji.to_dict() == self.gitmoji_dict


class TestGitmojiList:
    @pytest.fixture(autouse=True)
    def _mock_gitmoji_list_data(self):
        self.gitmoji_dicts = [
            {
                "emoji": "💥",
                "entity": "&#x1f4a5;",
                "code": ":boom:",
                "description": "Introduce breaking changes.",
                "name": "boom",
                "semver": "major",
            },
            {
                "emoji": "✨",
                "entity": "&#x2728;",
                "code": ":sparkles:",
                "description": "Introduce new features.",
                "name": "sparkles",
                "semver": "minor",
            },
            {
                "emoji": "🐛",
                "entity": "&#x1f41b;",
                "code": ":bug:",
                "description": "Fix a bug.",
                "name": "bug",
                "semver": "patch",
            },
            {
                "emoji": "📝",
                "entity": "&#x1f4dd;",
                "code": ":memo:",
                "description": "Add or update documentation.",
                "name": "memo",
                "semver": None,
            },
        ]
        self.gitmoji_list = GitmojiList(
            [Gitmoji.from_dict(gitmoji_dict) for gitmoji_dict in self.gitmoji_dicts]
        )

    def test_can_be_casted_to_set(self):
        try:
            set(self.gitmoji_list)
        except TypeError:
            pytest.fail(
                f"{self.gitmoji_list.__class__.__name__} mustn't be casted to set."
            )

    @pytest.mark.parametrize(
        ("index", "data_index"),
        [
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            ("boom", 0),
            ("sparkles", 1),
            ("bug", 2),
            ("memo", 3),
        ],
    )
    def test_indexing_works_if_int_or_str_index(self, index, data_index):
        gitmoji_indexed = self.gitmoji_list[index]

        assert isinstance(gitmoji_indexed, Gitmoji)
        assert gitmoji_indexed == self.gitmoji_list.data[data_index]

    def test_indexing_fails_if_invalid_index(self):
        with pytest.raises(GitmojiListIndexError):
            self.gitmoji_list["does_not_exist"]

        with pytest.raises(GitmojiListIndexError) as exc_info:
            self.gitmoji_list[len(self.gitmoji_list)]
        assert isinstance(exc_info.value.__cause__, IndexError)

    def test_indexing_works_with_updated_index_field(self, mocker):
        mocker.patch.object(GitmojiList, "_index_fields", ("code",))

        for gitmoji in self.gitmoji_list:
            assert self.gitmoji_list[gitmoji.code] == gitmoji

    @pytest.mark.parametrize(
        ("index", "data_index"),
        [
            (slice(0, 1), (0,)),
            (slice(1, 3), (1, 2)),
            (slice(1, 4, 2), (1, 3)),
        ],
    )
    def test_slicing_works_if_valid_slices(self, index, data_index):
        gitmojis_indexed = self.gitmoji_list[index]

        assert isinstance(gitmojis_indexed, GitmojiList)
        assert gitmojis_indexed.data == [self.gitmoji_list.data[i] for i in data_index]

    @pytest.mark.parametrize("field_name", Gitmoji.__dataclass_fields__.keys())
    def test_iter_field_works(self, field_name):
        iterator = self.gitmoji_list.iter_field(field_name)

        assert [*iterator] == [
            getattr(gitmoji, field_name) for gitmoji in self.gitmoji_list.data
        ]

    def test_iter_field_fails_if_invalid_field_name(self):
        with pytest.raises(GitmojiListAttributeError):
            self.gitmoji_list.iter_field("does_not_exist")

    def test_iter_fields_works_if_subset_of_fields(self):
        iterator = self.gitmoji_list.iter_fields("emoji", "code")

        assert list(iterator) == [
            ("💥", ":boom:"),
            ("✨", ":sparkles:"),
            ("🐛", ":bug:"),
            ("📝", ":memo:"),
        ]

    def test_iter_fields_works_if_all_fields(self):
        iterator = self.gitmoji_list.iter_fields()

        assert all(
            item == astuple(gitmoji)
            for item, gitmoji in zip(iterator, self.gitmoji_list)
        )
