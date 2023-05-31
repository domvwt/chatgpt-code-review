# ChatGPT Code Review

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://domvwt-chatgpt-code-review-chatgpt-code-reviewmain-cfe8uj.streamlit.app/)

[ChatGPT Code Review](https://domvwt-chatgpt-code-review-chatgpt-code-reviewmain-cfe8uj.streamlit.app/) is an app designed to help software developers improve
their code quality by leveraging the power of OpenAI's large language models.
The app analyzes the code in a given GitHub repository and provides
recommendations to enhance the code. It is a valuable tool for developers,
allowing them to discover potential issues in their codebase.

To use ChatGPT Code Review and get recommendations for your code, follow these
steps:

1. **Access the app**: Open the ChatGPT Code Review app in your web browser.
2. **Enter the GitHub repository URL**: In the input field labeled "GitHub
   Repository URL", enter the URL of the repository you'd like to analyze.
3. **Enter your OpenAI API Key**: In the input field labeled "OpenAI API Key",
   enter your OpenAI API key. If you don't have one, you can obtain it from the
   [OpenAI platform](https://platform.openai.com/account/api-keys).
4. **Select file extensions**: Choose the file extensions you want to analyze
   or add additional extensions in the provided input field.
5. **Clone the repository**: Click the "Clone Repository" button. The app will
   display the files available for analysis in a tree structure.
6. **Select files to analyze**: Check the boxes next to the files you want to
   analyze, then click the "Analyze Files" button.
7. **Review the recommendations**: The recommendations will be displayed in a
   clear and structured format, with code snippets and suggested improvements.
   Review these recommendations to identify potential areas for improvement in
   your code.

Keep in mind that ChatGPT Code Review is an AI-powered tool, and while it can
provide helpful insights, it may not always be perfect. It is essential to use
your judgment and expertise when assessing the recommendations provided by the
app.

## Example

<p width=100%>
<img width=100%  src="https://github.com/domvwt/chatgpt-code-review/blob/main/media/example.png?raw=true" alt="example page" style="border-radius:0.5%;">
</p>

## Installation and Usage

Here's how to install and use ChatGPT Code Review on your local machine:

1. **Clone the repository**: Execute this on your local machine and navigate to the project directory:

   ```bash
   git clone https://github.com/domvwt/chatgpt-code-review.git
   cd chatgpt-code-review
   ```

2. **Set up a virtual environment**: Run this command to establish a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

3. **Switch on the virtual environment**: Use the corresponding command to activate your virtual environment:

   ```bash
   source .venv/bin/activate  # Linux or macOS
   .venv\Scripts\activate  # Windows
   ```

4. **Deploy the application**: Use this command to install the app and its dependencies:

   ```bash
   pip install -e .
   ```

5. **Launch the app**: To get the app running, use this command:

   ```bash
   streamlit run chatgpt_code_review/app.py
   ```
