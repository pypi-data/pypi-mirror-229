from pathlib import Path

import git


class BranchNotFound(Exception):
    def __init__(self, branch_name):
        super().__init__(f'Branch not found: {branch_name}')
        self.branch_name = branch_name


def branch_exists(repo: git.Repo, branch_name):
    branch_names = [b.name for b in repo.branches]
    return branch_name in branch_names


def get_diff_paths(repo_path: Path, compare_branch: str) -> list[str]:
    repo = git.Repo(repo_path)
    if not branch_exists(repo, compare_branch):
        raise BranchNotFound(compare_branch)
    diff = repo.git.diff(compare_branch, repo.active_branch.name, name_only=True)
    return diff.split("\n") if diff else []
