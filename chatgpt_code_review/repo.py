import os
from typing import Iterable

import streamlit as st
from git import Repo


def list_code_files_in_repository(
    repo_url: str, extensions: list[str]
) -> Iterable[str]:
    """Clone the GitHub repository and return a list of code files with the specified extensions."""
    local_path = clone_github_repository(repo_url)
    return get_all_files_in_directory(local_path, extensions)


@st.cache_data(show_spinner=False)
def clone_github_repository(repo_url: str) -> str:
    """Clone a GitHub repository and return the local path."""
    local_path = repo_url.split("/")[-1]

    if not os.path.exists(local_path):
        Repo.clone_from(repo_url, local_path)

    return local_path


def get_all_files_in_directory(path: str, extensions: list[str]) -> list[str]:
    """Return a list of all files in a directory with the specified extension."""
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files


def create_file_tree(code_files: Iterable[str]) -> list[dict[str, str]]:
    file_tree = []
    code_files = sorted(code_files)
    for file in code_files:
        parts = file.split(os.sep)
        current_level = file_tree
        for i, part in enumerate(parts):
            existing = [
                node for node in current_level if node["label"] == part
            ]
            if existing:
                current_level = existing[0].setdefault("children", [])
            else:
                new_node = {
                    "label": part,
                    "value": os.sep.join(parts[: i + 1]),
                }
                current_level.append(new_node)
                if i != len(parts) - 1:
                    current_level = new_node.setdefault("children", [])
    return file_tree
