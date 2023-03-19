import logging
import os

import display
import openai
import query
import repo
import streamlit as st
from about import about_section
from streamlit_tree_select import tree_select


def load_environment_variables(file_path: str) -> None:
    if os.path.exists(file_path):
        with open(file_path) as f:
            for line in f:
                if line.strip():
                    key, value = line.strip().split("=")
                    os.environ[key] = value


def configure_logging(log_file: str, level: int = logging.INFO) -> None:
    logging.basicConfig(filename=log_file, level=level)


env_file_path = ".env"
log_file = "app.log"

load_environment_variables(env_file_path)
configure_logging(log_file)

cwd = os.getcwd()
temp_dir = "/tmp/chatgpt-code-review"
os.makedirs(temp_dir, exist_ok=True)
os.chdir(temp_dir)

st.set_page_config(
    page_title="ChatGPT Code Review",
)

session_state = st.session_state

st.title("ChatGPT Code Review :rocket:")

with st.expander("About ChatGPT Code Review"):
    st.markdown(about_section, unsafe_allow_html=True)
    st.write("")

with st.form("repo_url_form"):
    clone_repo_button = False
    # Get the GitHub repository URL
    default_repo_url = "https://github.com/domvwt/chatgpt-code-review"
    repo_url = st.text_input("GitHub Repository URL:", default_repo_url)

    # Get the OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY", "")
    openai.api_key = st.text_input(
        "OpenAI API Key:", api_key, placeholder="Paste your API key here"
    )

    # Set the maximum as integer input
    max_tokens = st.number_input(
        "Maximum tokens per OpenAI API query",
        min_value=1,
        max_value=4096,
        value=2000,
    )

    # Select file extensions to analyze
    options = [
        ".py",
        ".js",
        ".java",
        ".scala",
        ".cpp",
        ".c",
        ".cs",
        ".go",
        ".php",
        ".rb",
    ]
    extensions = st.multiselect(
        "File extensions to analyze",
        options=options,
        default=options,
    )
    additional_extensions = st.text_input(
        "Additional file extensions to analyze (comma-separated):"
    )
    if additional_extensions:
        extensions.extend(
            [ext.strip() for ext in additional_extensions.split(",")]
        )

    clone_repo_button = st.form_submit_button("Clone Repository")


# Clone the repository and display the list of files
with st.form("analyze_files_form"):
    analyze_files_button = False
    if clone_repo_button or session_state.get("code_files"):
        if not session_state.get("code_files"):
            session_state.code_files = repo.list_code_files_in_repository(
                repo_url, extensions
            )

        st.write("Select files to analyze:")
        file_tree = repo.create_file_tree(session_state.code_files)
        session_state.selected_files = tree_select(
            file_tree,
            show_expand_all=True,
            check_model="leaf",
            checked=session_state.get("selected_files"),
        )["checked"]
        logging.info("Selected files: %s", session_state.selected_files)
        analyze_files_button = st.form_submit_button("Analyze Files")


# Analyze the selected files
with st.spinner("Analyzing files..."):
    if analyze_files_button or session_state.get("analyzed_files"):
        session_state.analyzed_files = True
        if not openai.api_key:
            st.error("Please enter your OpenAI API key.")
            st.stop()

        if session_state.get("selected_files"):
            recommendations = query.analyze_code_files(
                session_state.selected_files, int(max_tokens)
            )

            # Display the recommendations
            st.header("Recommendations")
            first = True
            recommendation_list = []
            for rec in recommendations:
                if not first:
                    st.write("---")
                else:
                    first = False
                st.subheader(display.escape_markdown(rec["code_file"]))
                recommendation = rec["recommendation"] or "No recommendations"
                st.markdown(recommendation)
                with st.expander("View Code"):
                    extension = os.path.splitext(rec["code_file"])[1]
                    display.display_code(rec["code_snippet"], extension)
                recommendation_list.append(rec)
            if recommendation_list:
                session_state.recommendation_list = recommendation_list
        else:
            st.error("Please select at least one file to analyze.")
            st.stop()

st.write("")


def download_markdown(recommendations):
    if recommendations:
        st.download_button(
            "Download Markdown",
            data=display.generate_markdown(recommendations),
            file_name="chatgpt_recommendations.md",
            mime="text/markdown",
        )
    else:
        st.download_button(
            "Download Markdown",
            data="",
            file_name="chatgpt_recommendations.md",
            mime="text/markdown",
            disabled=True,
        )


download_markdown(session_state.get("recommendation_list"))

os.chdir(cwd)
