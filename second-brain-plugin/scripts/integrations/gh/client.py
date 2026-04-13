"""
GitHub API client — PRs, issues, diffs, and reviews via PyGithub.

Auth handled by auth.py. LLM never sees the token.
"""

from dataclasses import dataclass

from .auth import get_client


@dataclass
class PullRequest:
    number: int
    title: str
    author: str
    state: str
    created_at: str
    updated_at: str
    url: str
    additions: int
    deletions: int
    changed_files: int
    body: str = ""


@dataclass
class Issue:
    number: int
    title: str
    author: str
    state: str
    created_at: str
    labels: list[str]
    url: str
    body: str = ""


@dataclass
class FileChange:
    filename: str
    status: str  # added, removed, modified, renamed
    additions: int
    deletions: int
    patch: str


def list_prs(repo_name: str, state: str = "open", limit: int = 20) -> list[PullRequest]:
    """List pull requests for a repo."""
    g = get_client()
    repo = g.get_repo(repo_name)
    pulls = repo.get_pulls(state=state, sort="created", direction="desc")

    results = []
    for pr in pulls[:limit]:
        results.append(PullRequest(
            number=pr.number,
            title=pr.title,
            author=pr.user.login if pr.user else "unknown",
            state=pr.state,
            created_at=pr.created_at.isoformat(),
            updated_at=pr.updated_at.isoformat(),
            url=pr.html_url,
            additions=pr.additions,
            deletions=pr.deletions,
            changed_files=pr.changed_files,
            body=pr.body or "",
        ))

    return results


def get_pr_diff(repo_name: str, pr_number: int) -> list[FileChange]:
    """Get the file changes (diff) for a pull request."""
    g = get_client()
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    files = pr.get_files()

    return [
        FileChange(
            filename=f.filename,
            status=f.status,
            additions=f.additions,
            deletions=f.deletions,
            patch=f.patch or "",
        )
        for f in files
    ]


def list_issues(repo_name: str, state: str = "open", labels: list[str] | None = None, limit: int = 20) -> list[Issue]:
    """List issues (excluding PRs) for a repo."""
    g = get_client()
    repo = g.get_repo(repo_name)

    kwargs = {"state": state, "sort": "created", "direction": "desc"}
    if labels:
        kwargs["labels"] = [repo.get_label(l) for l in labels]

    all_issues = repo.get_issues(**kwargs)

    results = []
    for issue in all_issues[:limit * 2]:  # fetch extra since we filter out PRs
        if issue.pull_request:
            continue  # skip PRs (issues API returns both)
        results.append(Issue(
            number=issue.number,
            title=issue.title,
            author=issue.user.login if issue.user else "unknown",
            state=issue.state,
            created_at=issue.created_at.isoformat(),
            labels=[l.name for l in issue.labels],
            url=issue.html_url,
            body=issue.body or "",
        ))
        if len(results) >= limit:
            break

    return results


def create_review(repo_name: str, pr_number: int, body: str, event: str = "COMMENT"):
    """Create a review on a PR. Event: COMMENT, APPROVE, or REQUEST_CHANGES."""
    g = get_client()
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_review(body=body, event=event)
    return {"pr": pr_number, "event": event}


def get_rate_limit() -> dict:
    """Check current rate limit status."""
    g = get_client()
    rate = g.get_rate_limit()
    core = rate.rate  # PyGithub uses .rate for core rate limit
    return {
        "core_remaining": core.remaining,
        "core_limit": core.limit,
        "core_reset": core.reset.isoformat(),
    }


def format_pr_list(prs: list[PullRequest]) -> str:
    """Format PR list for display."""
    if not prs:
        return "No pull requests found."

    lines = []
    for pr in prs:
        lines.append(f"#{pr.number} [{pr.state}] {pr.title}")
        lines.append(f"  Author: {pr.author}  |  +{pr.additions} -{pr.deletions}  |  {pr.changed_files} files")
        lines.append(f"  Created: {pr.created_at}  |  {pr.url}")
        lines.append("")

    return "\n".join(lines)


def format_diff(files: list[FileChange]) -> str:
    """Format file changes for display."""
    if not files:
        return "No file changes."

    lines = []
    for f in files:
        lines.append(f"[{f.status}] {f.filename}  (+{f.additions} -{f.deletions})")
        if f.patch:
            # Show first 30 lines of patch
            patch_lines = f.patch.split("\n")[:30]
            for pl in patch_lines:
                lines.append(f"  {pl}")
            if len(f.patch.split("\n")) > 30:
                lines.append("  ... (truncated)")
        lines.append("")

    return "\n".join(lines)


def format_issue_list(issues: list[Issue]) -> str:
    """Format issue list for display."""
    if not issues:
        return "No issues found."

    lines = []
    for issue in issues:
        label_str = ", ".join(issue.labels) if issue.labels else "none"
        lines.append(f"#{issue.number} [{issue.state}] {issue.title}")
        lines.append(f"  Author: {issue.author}  |  Labels: {label_str}")
        lines.append(f"  Created: {issue.created_at}  |  {issue.url}")
        lines.append("")

    return "\n".join(lines)
