import json

import click

from gitmoji.core import load_gitmojis_from_api, load_gitmojis_from_json
from gitmoji.model import GitmojiList

from .constants import (
    DUMP_GITMOJI_API_JSON_PATH_DEV,
    DUMP_GITMOJI_API_JSON_PATH_LIB,
    DUMP_GITMOJI_API_PULL_REQUEST_BODY,
)
from .helpers import get_gitmoji_summary_message


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show the JSON file update summary, but do not make the actual dump.",
)
@click.option(
    "--dev",
    is_flag=True,
    help="Dump the API to the repository's backup, not the installed one.",
)
def dump_gitmoji_api(dry_run: bool, dev: bool) -> None:
    gitmojis_from_api = load_gitmojis_from_api()
    gitmojis_from_json = load_gitmojis_from_json()

    if gitmojis_from_api == gitmojis_from_json:
        click.echo("😎 The JSON backup is up-to-date with the Gitmoji API. ✅")
    else:
        added_gitmojis_message = get_gitmoji_summary_message(
            "### ➕ Added",
            GitmojiList(list(set(gitmojis_from_api) - set(gitmojis_from_json))),
        )
        removed_gitmojis_message = get_gitmoji_summary_message(
            "### ➖ Removed",
            GitmojiList(list(set(gitmojis_from_json) - set(gitmojis_from_api))),
        )
        click.echo(
            DUMP_GITMOJI_API_PULL_REQUEST_BODY.format(
                gitmojis_summary=("\n" * 2).join(
                    filter(None, [added_gitmojis_message, removed_gitmojis_message])
                )
            )
        )
        if not dry_run:
            if dev:
                gitmojis_json_path = DUMP_GITMOJI_API_JSON_PATH_DEV
            else:
                gitmojis_json_path = DUMP_GITMOJI_API_JSON_PATH_LIB

            gitmojis_json_content = {
                "gitmojis": [gitmoji.to_dict() for gitmoji in gitmojis_from_api]
            }

            with gitmojis_json_path.open("w", encoding="UTF-8") as fp:
                json.dump(gitmojis_json_content, fp, ensure_ascii=False, indent=2)

                # NOTE: Extra line added to avoid `end-of-file-fixer` hook errors!
                fp.write("\n")
