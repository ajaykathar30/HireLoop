"""
RecruitSight — Git Tools
Local Git operations via subprocess for repository analysis.
Replaces the Git MCP server approach with direct subprocess calls.
"""

import subprocess
import os
import re
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("recruitsight.git_tools")


def _run_git(repo_path: str, args: list[str], timeout: int = 60) -> str:
    """Run a git command in the given repo and return stdout."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            logger.warning(f"git {' '.join(args)} failed: {result.stderr.strip()}")
            return ""
        return result.stdout
    except subprocess.TimeoutExpired:
        logger.error(f"git {' '.join(args)} timed out after {timeout}s")
        return ""
    except FileNotFoundError:
        logger.error("git is not installed or not in PATH")
        return ""


def git_clone(repo_url: str, target_dir: str, timeout: int = 120) -> bool:
    """
    Clone a GitHub repository to the target directory.
    Returns True if successful, False otherwise.
    """
    try:
        # Remove target if it already exists
        if os.path.exists(target_dir):
            import shutil
            shutil.rmtree(target_dir, ignore_errors=True)

        result = subprocess.run(
            ["git", "clone", repo_url, target_dir],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            logger.error(f"git clone failed: {result.stderr.strip()}")
            return False

        # Unshallow to get full history for forensic analysis
        subprocess.run(
            ["git", "fetch", "--unshallow"],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
            errors="replace",
        )
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"git clone timed out after {timeout}s")
        return False
    except FileNotFoundError:
        logger.error("git is not installed or not in PATH")
        return False


def git_log(
    repo_path: str,
    max_count: int = 500,
    format_str: str = "%H|||%an|||%ae|||%aI|||%s",
) -> list[dict]:
    """
    Fetch the commit log with structured fields.
    Returns a list of dicts with: hash, author_name, author_email, date, message.
    """
    output = _run_git(
        repo_path,
        ["log", f"--max-count={max_count}", f"--format={format_str}", "--all"],
    )
    if not output.strip():
        return []

    commits = []
    for line in output.strip().split("\n"):
        parts = line.split("|||")
        if len(parts) >= 5:
            commits.append({
                "hash": parts[0],
                "author_name": parts[1],
                "author_email": parts[2],
                "date": parts[3],
                "message": parts[4],
            })
    return commits


def git_branch(repo_path: str) -> str:
    """Get the current/default branch name."""
    output = _run_git(repo_path, ["branch", "--show-current"])
    branch = output.strip()
    if not branch:
        # Fallback: try HEAD
        output = _run_git(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
        branch = output.strip()
    return branch or "main"


def git_status(repo_path: str) -> str:
    """Get git status output."""
    return _run_git(repo_path, ["status", "--porcelain"])


def git_show(repo_path: str, file_path: str, max_bytes: int = 50000) -> str:
    """
    Read the content of a file from the repository.
    Truncates at max_bytes to avoid memory issues with large files.
    """
    full_path = os.path.join(repo_path, file_path)
    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_bytes)
        if len(content) == max_bytes:
            content += "\n... [TRUNCATED]"
        return content
    except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
        logger.warning(f"Cannot read {file_path}: {e}")
        return ""


def git_diff(repo_path: str, commit_a: str, commit_b: str) -> str:
    """Get the diff between two commits."""
    output = _run_git(repo_path, ["diff", "--stat", commit_a, commit_b])
    return output


def git_diff_commit(repo_path: str, commit_hash: str) -> str:
    """Get the stat diff for a specific commit."""
    output = _run_git(repo_path, ["diff", "--stat", f"{commit_hash}~1", commit_hash])
    return output


def git_search_code(repo_path: str, pattern: str, max_results: int = 50) -> list[dict]:
    """
    Search for a pattern in the repository code.
    Returns list of dicts with: file, line_number, line_content.
    """
    output = _run_git(
        repo_path,
        ["grep", "-n", "-I", f"--max-count={max_results}", "-E", pattern],
    )
    if not output.strip():
        return []

    results = []
    for line in output.strip().split("\n")[:max_results]:
        # Format: file:line_number:content
        match = re.match(r"^(.+?):(\d+):(.*)$", line)
        if match:
            results.append({
                "file": match.group(1),
                "line_number": int(match.group(2)),
                "line_content": match.group(3).strip(),
            })
    return results


def get_directory_tree(repo_path: str, max_depth: int = 4) -> str:
    """
    Build a text representation of the directory tree.
    Excludes common non-essential directories (.git, node_modules, __pycache__, .venv).
    """
    exclude_dirs = {
        ".git", "node_modules", "__pycache__", ".venv", "venv",
        ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
        ".next", ".nuxt", "coverage", ".eggs",
    }
    exclude_files = {".DS_Store", "Thumbs.db"}

    lines = []
    root = Path(repo_path)

    def _walk(current: Path, prefix: str, depth: int):
        if depth > max_depth:
            return
        try:
            entries = sorted(current.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return

        # Filter
        entries = [
            e for e in entries
            if e.name not in exclude_dirs and e.name not in exclude_files
        ]

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            suffix = "/" if entry.is_dir() else ""
            lines.append(f"{prefix}{connector}{entry.name}{suffix}")

            if entry.is_dir():
                extension = "    " if is_last else "│   "
                _walk(entry, prefix + extension, depth + 1)

    lines.append(f"{root.name}/")
    _walk(root, "", 1)
    return "\n".join(lines)


def list_files(repo_path: str, max_files: int = 500) -> list[str]:
    """
    List all tracked files in the repository.
    Falls back to walking the directory if git ls-files fails.
    """
    output = _run_git(repo_path, ["ls-files"])
    if output.strip():
        files = output.strip().split("\n")[:max_files]
        return files

    # Fallback: walk the directory
    exclude_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv"}
    files = []
    for dirpath, dirnames, filenames in os.walk(repo_path):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for fname in filenames:
            rel_path = os.path.relpath(os.path.join(dirpath, fname), repo_path)
            files.append(rel_path)
            if len(files) >= max_files:
                return files
    return files


def get_file_extensions_summary(repo_path: str) -> dict[str, int]:
    """Count files by extension to determine primary languages."""
    files = list_files(repo_path)
    ext_counts: dict[str, int] = {}
    for f in files:
        ext = Path(f).suffix.lower()
        if ext:
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
    return dict(sorted(ext_counts.items(), key=lambda x: -x[1]))
