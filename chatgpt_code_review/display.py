import re
from typing import Optional

import streamlit as st
from utils import EXTENSION_TO_LANGUAGE_MAP


def extension_to_language(file_extension: str) -> Optional[str]:
    """Return the programming language corresponding to a given file extension."""
    return EXTENSION_TO_LANGUAGE_MAP.get(file_extension.lower(), None)


def display_code(code: str, extension: str) -> None:
    """Display the code snippet in the specified language."""
    language = extension_to_language(extension)
    markdown_code = f"```{language}\n{code}\n```"
    st.markdown(markdown_code)


def escape_markdown(text: str) -> str:
    """Escape markdown characters in a string."""
    escape_chars = [
        "\\",
        "`",
        "*",
        "_",
        "{",
        "}",
        "[",
        "]",
        "(",
        ")",
        "#",
        "+",
        "-",
        ".",
        "!",
    ]
    regex = re.compile("|".join(map(re.escape, escape_chars)))
    return regex.sub(r"\\\g<0>", text)


def generate_markdown(recommendations):
    markdown_str = "# ChatGPT Code Review Recommendations\n\n"

    for rec in recommendations:
        code_file = rec["code_file"]
        recommendation = rec["recommendation"] or "No recommendations"

        markdown_str += f"## {code_file}\n\n"
        markdown_str += f"{recommendation}\n\n"

    return markdown_str
