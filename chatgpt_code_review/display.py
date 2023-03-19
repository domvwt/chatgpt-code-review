from typing import Optional

import streamlit as st


def extension_to_language(file_extension: str) -> Optional[str]:
    """Return the programming language corresponding to a given file extension."""
    language_map = {
        ".py": "python",
        ".js": "javascript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp",
        ".go": "go",
        ".swift": "swift",
        ".ts": "typescript",
        ".rs": "rust",
        ".kt": "kotlin",
        ".m": "objective-c",
    }
    return language_map.get(file_extension.lower(), None)


def display_code(code: str, extension: str):
    """Display the code snippet in the specified language."""
    language = extension_to_language(extension)
    markdown_code = f"```{language}\n{code}\n```"
    st.markdown(markdown_code, unsafe_allow_html=True)


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
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text
