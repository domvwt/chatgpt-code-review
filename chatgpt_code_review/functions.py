import logging
import os
from textwrap import dedent

import openai
import streamlit as st
from git import Repo


@st.cache_data(show_spinner=False)
def clone_github_repository(repo_url, local_path):
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
def analyze_code_file(code_file, max_tokens):
    with open(code_file, "r") as f:
        code_content = f.read()
    # Log length of code snippet
    logging.info("Read code file %s with length %d", code_file, len(code_content))
    # Ignore empty files
    if not code_content:
        return None
    try:
        analysis = get_analysis(code_content, max_tokens=max_tokens)
    except Exception as e:
        logging.error("Error analyzing code file %s: %s", code_file, e)
        analysis = "Error analyzing code file: " + str(e)
        analysis += "\n\n(You may need to increase the maximum tokens)"
    return {
        "code_file": code_file,
        "code_snippet": code_content,
        "recommendation": analysis,
    }


def get_recommendations(repo_url, max_tokens, extensions):
    # Analyze the repository
    if repo_url:
        local_path = repo_url.split("/")[-1]
        local_path = os.path.join("/tmp", local_path)
        # Clone the repository if it doesn't exist
        if not os.path.exists(local_path):
            clone_github_repository(repo_url, local_path)
        # Get code files in the repository
        code_files = []
        for ext in extensions:
            code_files.extend(get_all_files_in_directory(local_path, ext))
        # Analyze each code file
        for code_file in code_files:
            response = analyze_code_file(code_file, max_tokens)
            yield response


@st.cache_data(show_spinner=False)
def get_analysis(code, max_tokens=200):
    prompt = dedent(f"""\
        Analyze the code below and provide feedback on syntax and logical errors, code
        refactoring and quality, performance optimization, security vulnerabilities,
        and best practices. Please provide specific examples of improvements for each
        area. Be concise and focus on the most important issues.

        Use the following response format, replacing 'RESPONSE' with feedback:
        **Syntax and logical errors**: RESPONSE
        **Code refactoring and quality**: RESPONSE
        **Performance optimization**: RESPONSE
        **Security vulnerabilities**: RESPONSE
        **Best practices**: RESPONSE

        Code:
        ```{code}```

        Your review:"""
    )

    logging.info("Sending request to OpenAI API for code analysis")
    logging.info("Max tokens: %d", max_tokens)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": code},
        ],
        max_tokens=max_tokens,
        n=1,
        temperature=0.5,
    )
    logging.info("Received response from OpenAI API")

    # Get the assistant's response from the API response
    assistant_response = response.choices[0].message['content']

    return assistant_response.strip()


def extension_to_language(file_extension):
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


def display_code(code, extension):
    language = extension_to_language(extension)
    logging.info("Displaying code with language %s", language)
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
