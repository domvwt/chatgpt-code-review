import logging
from textwrap import dedent
from typing import Iterable

import openai
import streamlit as st
import tiktoken


def analyze_code_files(code_files: list[str]) -> Iterable[dict[str, str]]:
    """Analyze the selected code files and return recommendations."""
    return (analyze_code_file(code_file) for code_file in code_files)


def analyze_code_file(code_file: str) -> dict[str, str]:
    """Analyze a code file and return a dictionary with file information and recommendations."""
    with open(code_file, "r") as f:
        code_content = f.read()

    if not code_content:
        return {
            "code_file": code_file,
            "code_snippet": code_content,
            "recommendation": "No code found in file",
        }

    try:
        logging.info("Analyzing code file: %s", code_file)
        analysis = get_code_analysis(code_content)
    except Exception as e:
        logging.info("Error analyzing code file: %s", code_file)
        analysis = f"Error analyzing code file: {e}"

    return {
        "code_file": code_file,
        "code_snippet": code_content,
        "recommendation": analysis,
    }


def get_num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    # Source: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logging.debug("Model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        logging.debug(
            "gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301."
        )
        return get_num_tokens_from_messages(
            messages, model="gpt-3.5-turbo-0301"
        )
    elif model == "gpt-4":
        logging.debug(
            "gpt-4 may change over time. Returning num tokens assuming gpt-4-0314."
        )
        return get_num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


@st.cache_data(show_spinner=False)
def get_code_analysis(code: str) -> str:
    """Get code analysis from the OpenAI API."""
    prompt = dedent(
        f"""\
Please review the code below and identify any syntax or logical errors, suggest
ways to refactor and improve code quality, enhance performance, address security
concerns, and align with best practices. Provide specific examples for each area
and limit your recommendations to three per category.

Use the following response format, keeping the section headings as-is, and provide
your feedback. Use bullet points for each response. The provided examples are for
illustration purposes only and should not be repeated.

**Syntax and logical errors (example)**:
- Incorrect indentation on line 12
- Missing closing parenthesis on line 23

**Code refactoring and quality (example)**:
- Replace multiple if-else statements with a switch case for readability
- Extract repetitive code into separate functions

**Performance optimization (example)**:
- Use a more efficient sorting algorithm to reduce time complexity
- Cache results of expensive operations for reuse

**Security vulnerabilities (example)**:
- Sanitize user input to prevent SQL injection attacks
- Use prepared statements for database queries

**Best practices (example)**:
- Add meaningful comments and documentation to explain the code
- Follow consistent naming conventions for variables and functions

Code:
```
{code}
```

Your review:"""
    )
    messages = [{"role": "system", "content": prompt}]
    tokens_in_messages = get_num_tokens_from_messages(
        messages=messages, model="gpt-3.5-turbo"
    )
    max_tokens = 4096
    tokens_for_response = max_tokens - tokens_in_messages

    if tokens_for_response < 200:
        return "The code file is too long to analyze. Please select a shorter file."

    logging.info("Sending request to OpenAI API for code analysis")
    logging.info("Max response tokens: %d", tokens_for_response)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=tokens_for_response,
        n=1,
        temperature=0,
    )
    logging.info("Received response from OpenAI API")

    # Get the assistant's response from the API response
    assistant_response = response.choices[0].message["content"]

    return assistant_response.strip()
