import logging
import os

EXTENSION_TO_LANGUAGE_MAP = {
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


def load_environment_variables(file_path: str) -> None:
    if os.path.exists(file_path):
        with open(file_path) as f:
            for line in f:
                if line.strip():
                    key, value = line.strip().split("=")
                    os.environ[key] = value


def set_environment_variables() -> None:
    os.environ["TOKENIZERS_PARALLELISM"] = "false"


def configure_logging(log_file: str, level: int = logging.INFO) -> None:
    logging.basicConfig(filename=log_file, level=level)


class TempDirContext:
    def __init__(self, temp_dir: str) -> None:
        self.cwd = os.getcwd()
        self.temp_dir = temp_dir

    def __enter__(self):
        os.makedirs(self.temp_dir, exist_ok=True)
        os.chdir(self.temp_dir)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.cwd)
