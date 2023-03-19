import logging
import os

import openai
import streamlit as st
from about import about_section
from functions import display_code, escape_markdown, get_recommendations


env_file_path = ".env"

# Load all environment variables from the .env file
if os.path.exists(env_file_path):
    with open(env_file_path) as f:
        for line in f:
            if line.strip():
                key, value = line.strip().split("=")
                os.environ[key] = value

# Configure logging
log_file = "app.log"
logging.basicConfig(filename=log_file, level=logging.INFO)

st.set_page_config(
    page_title="ChatGPT Code Review",
)

analyze_repo_button = False

st.title("ChatGPT Code Review :rocket:")

with st.expander("About ChatGPT Code Review"):
    st.markdown(about_section, unsafe_allow_html=True)
    st.write("")

with st.form("repo_url_form"):
    # Get the GitHub repository URL
    default_repo_url = "https://github.com/domvwt/chatgpt-code-review"
    repo_url = st.text_input("GitHub Repository URL:", default_repo_url)

    # Get the OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY", "")
    openai.api_key = st.text_input("OpenAI API Key:", api_key, placeholder="Paste your API key here")

    # Set the maximum as integer input
    max_tokens = st.number_input(
        "Maximum tokens per OpenAI API query", min_value=1, max_value=4096, value=2000
    )

    # Select file extensions to analyze
    options = [".py", ".js", ".java", ".scala", ".cpp", ".c", ".cs", ".go", ".php", ".rb"]
    extensions = st.multiselect(
        "File extensions to analyze",
        options=options,
        default=options,
    )
    additional_extensions = st.text_input("Additional file extensions to analyze (comma-separated):")
    if additional_extensions:
        extensions.extend([ext.strip() for ext in additional_extensions.split(",")])

    analyze_repo_button = st.form_submit_button("Analyze Repository")

if analyze_repo_button:
    if not openai.api_key:
        st.error("Please enter your OpenAI API key.")
        st.stop()
    with st.spinner("Analyzing repository..."):
        if repo_url:
            recommendations = get_recommendations(repo_url, max_tokens, extensions)

            # Display the recommendations
            first = True
            for rec in filter(None, recommendations):
                if not first:
                    st.write("---")
                else:
                    st.header("Recommendations")
                    first = False
                subheader = escape_markdown(rec["code_file"]).replace("/tmp/", "")
                st.subheader(subheader)
                recommendation = rec["recommendation"] or "No recommendations"
                st.markdown(recommendation)
                # Expander to show the code
                with st.expander("View Code"):
                    extension = os.path.splitext(rec["code_file"])[1]
                    display_code(rec["code_snippet"], extension)
        else:
            st.error("Please enter a valid GitHub repository URL.")
