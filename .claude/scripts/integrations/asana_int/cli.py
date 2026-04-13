"""
Asana CLI subcommands.

Usage:
    asana tasks [--project <gid>] [--limit N]
    asana overdue [--workspace <gid>]
    asana upcoming [--days N] [--workspace <gid>]
    asana projects [--workspace <gid>]
"""

import argparse
import sys

from . import client


def main(args: list[str]):
    parser = argparse.ArgumentParser(prog="query.py asana", description="Asana integration")
    sub = parser.add_subparsers(dest="action", required=True)

    # tasks
    p_tasks = sub.add_parser("tasks", help="List tasks")
    p_tasks.add_argument("--project", default="", help="Project GID (omit for all my tasks)")
    p_tasks.add_argument("--limit", type=int, default=50)

    # overdue
    p_overdue = sub.add_parser("overdue", help="Show overdue tasks")
    p_overdue.add_argument("--workspace", default="", help="Workspace GID")

    # upcoming
    p_upcoming = sub.add_parser("upcoming", help="Show upcoming deadlines")
    p_upcoming.add_argument("--days", type=int, default=7, help="Days ahead (default: 7)")
    p_upcoming.add_argument("--workspace", default="", help="Workspace GID")

    # projects
    p_projects = sub.add_parser("projects", help="List projects")
    p_projects.add_argument("--workspace", default="", help="Workspace GID")

    parsed = parser.parse_args(args)

    if parsed.action == "tasks":
        tasks = client.list_tasks(project_gid=parsed.project, limit=parsed.limit)
        print(client.format_task_list(tasks))

    elif parsed.action == "overdue":
        tasks = client.get_overdue_tasks(workspace_gid=parsed.workspace)
        print(client.format_task_list(tasks, title="Overdue Tasks"))

    elif parsed.action == "upcoming":
        tasks = client.get_upcoming_tasks(days=parsed.days, workspace_gid=parsed.workspace)
        print(client.format_task_list(tasks, title=f"Due in {parsed.days} days"))

    elif parsed.action == "projects":
        projects = client.list_projects(workspace_gid=parsed.workspace)
        print(client.format_project_list(projects))
