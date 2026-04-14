"""
GitHub CLI subcommands.

Usage:
    github prs [--repo owner/repo] [--state open|closed|all]
    github issues [--repo owner/repo] [--labels bug,enhancement] [--state open]
    github diff <pr_number> [--repo owner/repo]
    github review <pr_number> --body <text> [--repo owner/repo] [--event COMMENT]
    github rate-limit
"""

import argparse
import sys

from . import client


def main(args: list[str]):
    parser = argparse.ArgumentParser(prog="query.py github", description="GitHub integration")
    sub = parser.add_subparsers(dest="action", required=True)

    # prs
    p_prs = sub.add_parser("prs", help="List pull requests")
    p_prs.add_argument("--repo", required=True, help="Repository (owner/repo)")
    p_prs.add_argument("--state", default="open", choices=["open", "closed", "all"])
    p_prs.add_argument("--limit", type=int, default=20)

    # issues
    p_issues = sub.add_parser("issues", help="List issues")
    p_issues.add_argument("--repo", required=True, help="Repository (owner/repo)")
    p_issues.add_argument("--state", default="open", choices=["open", "closed", "all"])
    p_issues.add_argument("--labels", default="", help="Comma-separated labels to filter")
    p_issues.add_argument("--limit", type=int, default=20)

    # diff
    p_diff = sub.add_parser("diff", help="Get PR file changes")
    p_diff.add_argument("pr_number", type=int, help="PR number")
    p_diff.add_argument("--repo", required=True, help="Repository (owner/repo)")

    # review
    p_review = sub.add_parser("review", help="Post a review on a PR")
    p_review.add_argument("pr_number", type=int, help="PR number")
    p_review.add_argument("--repo", required=True, help="Repository (owner/repo)")
    p_review.add_argument("--body", required=True, help="Review body text")
    p_review.add_argument("--event", default="COMMENT", choices=["COMMENT", "APPROVE", "REQUEST_CHANGES"])

    # rate-limit
    sub.add_parser("rate-limit", help="Check API rate limit status")

    parsed = parser.parse_args(args)

    if parsed.action == "prs":
        prs = client.list_prs(parsed.repo, state=parsed.state, limit=parsed.limit)
        print(client.format_pr_list(prs))

    elif parsed.action == "issues":
        labels = [l.strip() for l in parsed.labels.split(",") if l.strip()] if parsed.labels else None
        issues = client.list_issues(parsed.repo, state=parsed.state, labels=labels, limit=parsed.limit)
        print(client.format_issue_list(issues))

    elif parsed.action == "diff":
        files = client.get_pr_diff(parsed.repo, parsed.pr_number)
        print(client.format_diff(files))

    elif parsed.action == "review":
        result = client.create_review(parsed.repo, parsed.pr_number, body=parsed.body, event=parsed.event)
        print(f"Review posted on PR #{result['pr']} ({result['event']})")

    elif parsed.action == "rate-limit":
        rl = client.get_rate_limit()
        print(f"Core: {rl['core_remaining']}/{rl['core_limit']} (resets {rl['core_reset']})")
