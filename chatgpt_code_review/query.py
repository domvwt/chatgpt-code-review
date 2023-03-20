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
        Analyze the code below and provide feedback on syntax and logical errors, code
        refactoring and quality, performance optimization, security vulnerabilities,
        and best practices. Please provide specific examples of improvements for each
        area. Be concise and focus on the most important issues. Make sure to only provide
        accurate and relevant information. Do not offer feedback on functions that are
        not defined in the code. Assume that all required libraries are available.

        Use the following response format, strictly retaining the exact section headings
        and replacing 'RESPONSE' with feedback. Use bullet points for each response.

        **Syntax and logical errors**: RESPONSE
        **Code refactoring and quality**: RESPONSE
        **Performance optimization**: RESPONSE
        **Security vulnerabilities**: RESPONSE
        **Best practices**: RESPONSE

        Code:
        ```
        {code}
        ```

        Your review must adhere to the format above. Now, provide your review:"""
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
