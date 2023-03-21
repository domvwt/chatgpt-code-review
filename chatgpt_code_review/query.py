import logging
from textwrap import dedent
from typing import Iterable

import openai
import streamlit as st
import transformers as tf


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


@st.cache_resource(show_spinner=False)
def get_tokenizer() -> tf.GPT2Tokenizer:
    """Get the GPT-2 tokenizer."""
    return tf.GPT2TokenizerFast.from_pretrained("gpt2")


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
    tokenizer = get_tokenizer()
    tokens_in_prompt = len(tokenizer.encode(prompt))
    max_tokens = 4096
    tokens_for_response = max_tokens - tokens_in_prompt

    if tokens_for_response < 200:
        return "The code file is too long to analyze. Please select a shorter file."

    logging.info("Sending request to OpenAI API for code analysis")
    logging.info("Max response tokens: %d", tokens_for_response)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
        ],
        max_tokens=tokens_for_response,
        n=1,
        temperature=0,
    )
    logging.info("Received response from OpenAI API")

    # Get the assistant's response from the API response
    assistant_response = response.choices[0].message["content"]

    return assistant_response.strip()
