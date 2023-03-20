import logging
from textwrap import dedent
from typing import Iterable

import openai
import streamlit as st


def analyze_code_files(
    code_files: list[str], max_tokens: int
) -> Iterable[dict[str, str]]:
    """Analyze the selected code files and return recommendations."""
    return (
        analyze_code_file(code_file, max_tokens) for code_file in code_files
    )


def analyze_code_file(code_file: str, max_tokens: int) -> dict[str, str]:
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
        analysis = get_code_analysis(code_content, max_tokens=max_tokens)
    except Exception as e:
        analysis = f"Error analyzing code file: {e}\n\n(You may need to increase the maximum tokens)"

    return {
        "code_file": code_file,
        "code_snippet": code_content,
        "recommendation": analysis,
    }


@st.cache_data(show_spinner=False)
def get_code_analysis(code: str, max_tokens: int) -> str:
    """Get code analysis from the OpenAI API."""
    prompt = dedent(
        f"""\
        Analyze the code below and provide feedback on syntax and logical errors, code
        refactoring and quality, performance optimization, security vulnerabilities,
        and best practices. Please provide specific examples of improvements for each
        area. Be concise and focus on the most important issues. Make sure to only provide
        accurate and relevant information.

        Use the following response format, strictly retaining the exact section headings
        and replacing 'RESPONSE' with feedback. Use bullet points for each response.

        **Syntax and logical errors**: RESPONSE
        **Code refactoring and quality**: RESPONSE
        **Performance optimization**: RESPONSE
        **Security vulnerabilities**: RESPONSE
        **Best practices**: RESPONSE

        Code:
        ```{code}```

        Your review must adhere to the format above. Now, provide your review:"""
    )

    logging.info("Sending request to OpenAI API for code analysis")
    logging.info("Max tokens: %d", max_tokens)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            # {"role": "user", "content": code},
        ],
        max_tokens=max_tokens,
        n=1,
        temperature=0,
    )
    logging.info("Received response from OpenAI API")

    # Get the assistant's response from the API response
    assistant_response = response.choices[0].message["content"]

    return assistant_response.strip()
