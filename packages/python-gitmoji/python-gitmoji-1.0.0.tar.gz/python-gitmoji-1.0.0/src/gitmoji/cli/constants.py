from pathlib import Path

DUMP_GITMOJI_API_JSON_PATH_LIB = Path(__file__).parents[1] / "assets" / "gitmojis.json"

DUMP_GITMOJI_API_JSON_PATH_DEV = (
    Path.cwd() / "src" / "gitmoji" / "assets" / "gitmojis.json"
)

DUMP_GITMOJI_API_PULL_REQUEST_BODY = """## Gitmoji API dumped! 🎉

The official Gitmoji [API][gitmoji-api] has been dumped to the repo's backup file! 🗃️

{gitmojis_summary}

[gitmoji-api]: https://github.com/carloscuesta/gitmoji/tree/master/packages/gitmojis#api
"""
