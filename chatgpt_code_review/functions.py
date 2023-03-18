import logging
import os
from textwrap import dedent

import openai
import streamlit as st
from git import Repo


@st.cache_data
def clone_github_repository(repo_url, local_path):
    # Clone the GitHub repository
    try:
        repo = Repo.clone_from(repo_url, local_path)
        return repo
    except Exception:
        return None


def get_all_files_in_directory(path, extension):
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(extension):
                files.append(os.path.join(root, filename))
    return files


@st.cache_data(show_spinner=False)
def analyze_code_file(code_file):
    with open(code_file, "r") as f:
        code_snippet = f.read()
    # Log length of code snippet
    logging.info("Read code file %s with length %d", code_file, len(code_snippet))
    # Ignore empty files
    if not code_snippet:
        return None
    analysis = get_analysis(code_snippet)
    return {
        "code_file": code_file,
        "code_snippet": code_snippet,
        "recommendation": analysis,
    }


# Change spinner text to "Analyzing repository..."
@st.cache_data(show_spinner=False)
def get_recommendations(repo_url):
    # Analyze the repository
    recommendations = []
    if repo_url:
        local_path = repo_url.split("/")[-1]
        # Clone the repository if it doesn't exist
        if not os.path.exists(local_path):
            clone_github_repository(repo_url, local_path)
        # Get code files in the repository
        code_files = []
        extensions = [".py", ".js"]  # Add more extensions as needed
        for ext in extensions:
            code_files.extend(get_all_files_in_directory(local_path, ext))

        # Analyze each code file
        for code_file in code_files:
            response = analyze_code_file(code_file)
            if response:
                recommendations.append(response)

    return recommendations


@st.cache_data(show_spinner=False)
def get_analysis(code):
    prompt = dedent(
        f"""
    Analyze the code below and provide feedback on syntax and logical
    errors, code refactoring and quality, performance optimization, security
    vulnerabilities, and best practices. Please provide specific examples of
    improvements for each area.

    Code:
    ```{code}```
    """
    )

    logging.info("Sending request to OpenAI API for code analysis")
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0,
    )
    logging.info("Received response from OpenAI API")

    return response.choices[0].text.strip()


def display_code(code, language):
    markdown_code = f"```{language}\n{code}\n```"
    st.markdown(markdown_code, unsafe_allow_html=True)


def escape_markdown(text):
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
