from typing import List, TypedDict
from github import Github
import base64

class CodeChange(TypedDict):
    file_path: str
    line_number: int
    old_code: str
    new_code: str
    change_type: str # 'addition', 'deletion', 'modification'

class ReviewComment(TypedDict):
    file_path: str
    line_number: int
    comment: str
    severity: str # 'low', 'medium', 'high', 'critical'
    category: str # 'style', 'security', 'performance', 'best_practice'

class ReviewBot(TypedDict):
    code_changes: List[CodeChange]
    review_comments: List[ReviewComment]
    summary: str
    severity_level: str
    suggestions: List[str]
    patterns: List[str]
    excluded_patterns: List[str]
    human_feedback: str
    user_satisfied: bool
    followup_response: str
    feedback_rounds: int

DEFAULT_EXCLUDED = [
    "*.pyc", "__pycache__", ".git", ".venv", "venv", "node_modules", 
    ".env", "*.log", "package-lock.json", "pnpm-lock.yaml", "bun.lock", "bun.lockb", "yarn.lock","cargo.lock", "*.tmp", 
    ".DS_Store", "target", "*.egg-info", "dist", "build"
]

def get_github_repo(repo_name: str, token: str):
    """Connect to GitHub repository"""
    g = Github(token)
    return g.get_repo(repo_name)

def get_file_content(repo, file_path: str, ref: str = "main"):
    """Get file content from GitHub"""
    try:
        file = repo.get_contents(file_path, ref=ref)
        if isinstance(file, list):
            return None
        return base64.b64decode(file.content).decode("utf-8")
    except:
        return None

def get_repository_files(repo, path: str = "", ref: str = "main"):
    """Get all files from repository"""
    files = []
    try:
        contents = repo.get_contents(path, ref=ref)
        for item in contents:
            if item.type == "file":
                files.append({
                    "path": item.path,
                    "content": get_file_content(repo, item.path, ref),
                    "sha": item.sha
                })
            elif item.type == "dir":
                files.extend(get_repository_files(repo, item.path, ref))
    except:
        pass
    return files
