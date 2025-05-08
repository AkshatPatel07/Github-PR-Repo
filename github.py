from github import Github
from typing import Tuple

def init_github_client(token: str) -> Github:
    return Github(token)

def get_pr_diff(client: Github, repo_full_name: str, pr_number: int) -> Tuple[str, str]:
    repo = client.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)

    title = pr.title
    diff_text = ""

    files = pr.get_files()

    for file in files:
        filename = file.filename
        patch = file.patch or ""
        diff_text += f"--- {filename} ---\n {patch}\n\n"
    
    return title, diff_text