import os

import about
import display
import download
import forms
import query
import repo
import streamlit as st
import utils

env_file_path = ".env"
log_file = "app.log"


temp_dir = "/tmp/chatgpt-code-review"


def app():
    utils.load_environment_variables(env_file_path)
    utils.set_environment_variables()
    utils.configure_logging(log_file)

    with utils.TempDirContext(temp_dir):
        st.set_page_config(
            page_title="ChatGPT Code Review",
        )

        session_state = st.session_state

        st.title("ChatGPT Code Review :rocket:")

        with st.expander("About ChatGPT Code Review"):
            st.markdown(about.about_section, unsafe_allow_html=True)
            st.write("")

        default_repo_url = "https://github.com/domvwt/chatgpt-code-review"
        repo_form = forms.RepoForm(default_repo_url)
        with st.form("repo_url_form"):
            repo_form.display_form()

        # Check if the API key is valid before proceeding
        if repo_form.clone_repo_button and not repo_form.is_api_key_valid():
            st.stop()

        repo_url, extensions = repo_form.get_form_data()

        analyze_files_form = forms.AnalyzeFilesForm(session_state)
        with st.form("analyze_files_form"):
            if repo_form.clone_repo_button or session_state.get("code_files"):
                if not session_state.get("code_files"):
                    session_state.code_files = (
                        repo.list_code_files_in_repository(
                            repo_url, extensions
                        )
                    )

                analyze_files_form.display_form()

        # Analyze the selected files
        with st.spinner("Analyzing files..."):
            if session_state.get("analyze_files"):
                if session_state.get("selected_files"):
                    recommendations = query.analyze_code_files(
                        session_state.selected_files
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
                        recommendation = (
                            rec["recommendation"] or "No recommendations"
                        )
                        st.markdown(recommendation)
                        with st.expander("View Code"):
                            extension = os.path.splitext(rec["code_file"])[1]
                            display.display_code(
                                rec["code_snippet"], extension
                            )
                        recommendation_list.append(rec)
                    if recommendation_list:
                        session_state.recommendation_list = recommendation_list
                else:
                    st.error("Please select at least one file to analyze.")
                    st.stop()

        st.write("")

        download.download_markdown(session_state.get("recommendation_list"))


if __name__ == "__main__":
    app()
