from ..model import GitmojiList


def get_gitmoji_summary_message(header: str, gitmojis: GitmojiList) -> str:
    if not gitmojis:
        return ""
    for index, gitmoji in enumerate(gitmojis):
        if index == 0:
            message = f"{header}\n\n"
        message += f"* {gitmoji.emoji} `{gitmoji.code}` &ndash; {gitmoji.description}"
        if index < len(gitmojis) - 1:
            message += "\n"
    return message
