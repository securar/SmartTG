from __future__ import annotations

import html
import re
from typing import Pattern

__all__ = (
    "HtmlDecoration",
    "MarkdownDecoration",
    "html_decoration",
    "markdown_decoration",
    "add_surrogates",
    "remove_surrogates",
)


def add_surrogates(text: str) -> bytes:
    return text.encode("utf-16-le")


def remove_surrogates(text: bytes) -> str:
    return text.decode("utf-16-le")


class HtmlDecoration:
    BOLD_TAG = "b"
    ITALIC_TAG = "i"
    UNDERLINE_TAG = "u"
    STRIKETHROUGH_TAG = "s"
    SPOILER_TAG = "tg-spoiler"
    EMOJI_TAG = "tg-emoji"
    BLOCKQUOTE_TAG = "blockquote"

    @staticmethod
    def link(value: str, link: str) -> str:
        return f'<a href="{link}">{value}</a>'

    def bold(self, value: str) -> str:
        return f"<{self.BOLD_TAG}>{value}</{self.BOLD_TAG}>"

    def italic(self, value: str) -> str:
        return f"<{self.ITALIC_TAG}>{value}</{self.ITALIC_TAG}>"

    @staticmethod
    def code(value: str) -> str:
        return f"<code>{value}</code>"

    @staticmethod
    def pre(value: str) -> str:
        return f"<pre>{value}</pre>"

    @staticmethod
    def pre_language(value: str, language: str) -> str:
        return f'<pre><code class="language-{language}">{value}</code></pre>'

    def underline(self, value: str) -> str:
        return f"<{self.UNDERLINE_TAG}>{value}</{self.UNDERLINE_TAG}>"

    def strikethrough(self, value: str) -> str:
        return f"<{self.STRIKETHROUGH_TAG}>{value}</{self.STRIKETHROUGH_TAG}>"

    def spoiler(self, value: str) -> str:
        return f"<{self.SPOILER_TAG}>{value}</{self.SPOILER_TAG}>"

    @staticmethod
    def quote(value: str) -> str:
        return html.escape(value, quote=False)

    def custom_emoji(self, value: str, custom_emoji_id: str) -> str:
        return f'<{self.EMOJI_TAG} emoji-id="{custom_emoji_id}">{value}</tg-emoji>'

    def blockquote(self, value: str) -> str:
        return f"<{self.BLOCKQUOTE_TAG}>{value}</{self.BLOCKQUOTE_TAG}>"

    def expandable_blockquote(self, value: str) -> str:
        return f"<{self.BLOCKQUOTE_TAG} expandable>{value}</{self.BLOCKQUOTE_TAG}>"


class MarkdownDecoration:
    MARKDOWN_QUOTE_PATTERN: Pattern[str] = re.compile(r"([_*\[\]()~`>#+\-=|{}.!\\])")

    @staticmethod
    def link(value: str, link: str) -> str:
        return f"[{value}]({link})"

    @staticmethod
    def bold(value: str) -> str:
        return f"*{value}*"

    @staticmethod
    def italic(value: str) -> str:
        return f"_\r{value}_\r"

    @staticmethod
    def code(value: str) -> str:
        return f"`{value}`"

    @staticmethod
    def pre(value: str) -> str:
        return f"```\n{value}\n```"

    @staticmethod
    def pre_language(value: str, language: str) -> str:
        return f"```{language}\n{value}\n```"

    @staticmethod
    def underline(value: str) -> str:
        return f"__\r{value}__\r"

    @staticmethod
    def strikethrough(value: str) -> str:
        return f"~{value}~"

    @staticmethod
    def spoiler(value: str) -> str:
        return f"||{value}||"

    def quote(self, value: str) -> str:
        return re.sub(pattern=self.MARKDOWN_QUOTE_PATTERN, repl=r"\\\1", string=value)

    def custom_emoji(self, value: str, custom_emoji_id: str) -> str:
        return f'!{self.link(value=value, link=f"tg://emoji?id={custom_emoji_id}")}'

    @staticmethod
    def blockquote(value: str) -> str:
        return "\n".join(f">{line}" for line in value.splitlines())

    @staticmethod
    def expandable_blockquote(value: str) -> str:
        return "\n".join(f">{line}" for line in value.splitlines()) + "||"


html_decoration = HtmlDecoration()
markdown_decoration = MarkdownDecoration()
