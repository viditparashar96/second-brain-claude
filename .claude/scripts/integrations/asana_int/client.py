"""
Asana API client — Tasks, deadlines, projects via official SDK v5.

Auth handled by auth.py. LLM never sees the token.
"""

from dataclasses import dataclass
from datetime import date, timedelta

import asana
from asana.rest import ApiException

from .auth import get_api_client


@dataclass
class Task:
    gid: str
    name: str
    completed: bool
    due_on: str  # YYYY-MM-DD or ""
    due_at: str  # ISO datetime or ""
    assignee: str
    project: str
    notes: str = ""


@dataclass
class Project:
    gid: str
    name: str
    owner: str
    due_on: str


def _get_workspace_gid(api_client: asana.ApiClient) -> str:
    """Get the first workspace GID for the authenticated user."""
    workspaces_api = asana.WorkspacesApi(api_client)
    workspaces = workspaces_api.get_workspaces(opts={})
    for ws in workspaces:
        return ws["gid"]
    raise ValueError("No Asana workspaces found for this token.")


def _parse_task(t: dict) -> Task:
    """Parse an Asana task dict into a Task dataclass."""
    assignee = ""
    if t.get("assignee"):
        assignee = t["assignee"].get("name", t["assignee"].get("gid", ""))

    project = ""
    if t.get("projects"):
        project = t["projects"][0].get("name", "") if isinstance(t["projects"], list) and t["projects"] else ""
    elif t.get("memberships"):
        for m in t.get("memberships", []):
            if m.get("project", {}).get("name"):
                project = m["project"]["name"]
                break

    return Task(
        gid=t.get("gid", ""),
        name=t.get("name", ""),
        completed=t.get("completed", False),
        due_on=t.get("due_on", "") or "",
        due_at=t.get("due_at", "") or "",
        assignee=assignee,
        project=project,
        notes=t.get("notes", "") or "",
    )


def list_tasks(project_gid: str = "", limit: int = 50) -> list[Task]:
    """List tasks in a project, or all tasks assigned to me if no project."""
    api_client = get_api_client()
    tasks_api = asana.TasksApi(api_client)

    opts = {
        "opt_fields": "name,completed,due_on,due_at,assignee.name,notes,memberships.project.name",
        "limit": limit,
    }

    if project_gid:
        opts["project"] = project_gid
        result = tasks_api.get_tasks(opts=opts)
    else:
        # Get tasks assigned to me
        users_api = asana.UsersApi(api_client)
        me = users_api.get_user("me", opts={})
        workspace_gid = _get_workspace_gid(api_client)
        opts["assignee"] = me["gid"]
        opts["workspace"] = workspace_gid
        result = tasks_api.get_tasks(opts=opts)

    tasks = []
    for t in result:
        tasks.append(_parse_task(t))
        if len(tasks) >= limit:
            break

    return tasks


def get_overdue_tasks(workspace_gid: str = "") -> list[Task]:
    """Get tasks that are overdue (due before today, not completed).

    Uses search API on paid workspaces, falls back to client-side filtering on free tier.
    """
    api_client = get_api_client()

    if not workspace_gid:
        workspace_gid = _get_workspace_gid(api_client)

    tasks_api = asana.TasksApi(api_client)
    today = date.today().isoformat()

    try:
        # Try search API (paid workspaces only)
        result = tasks_api.search_tasks_for_workspace(
            workspace_gid=workspace_gid,
            opts={
                "due_on.before": today,
                "completed": False,
                "sort_by": "due_date",
                "sort_ascending": True,
                "opt_fields": "name,completed,due_on,due_at,assignee.name,memberships.project.name",
            },
        )
        return [_parse_task(t) for t in result]

    except ApiException as e:
        if e.status == 402:
            # Free tier — fall back to client-side filtering
            return _overdue_fallback(api_client, workspace_gid, today)
        raise


def _overdue_fallback(api_client: asana.ApiClient, workspace_gid: str, today: str) -> list[Task]:
    """Fallback for free-tier: get my incomplete tasks and filter client-side."""
    tasks_api = asana.TasksApi(api_client)
    users_api = asana.UsersApi(api_client)
    me = users_api.get_user("me", opts={})

    result = tasks_api.get_tasks(opts={
        "assignee": me["gid"],
        "workspace": workspace_gid,
        "completed_since": "now",
        "opt_fields": "name,completed,due_on,due_at,assignee.name,memberships.project.name",
    })

    overdue = []
    for t in result:
        task = _parse_task(t)
        if not task.completed and task.due_on and task.due_on < today:
            overdue.append(task)

    return sorted(overdue, key=lambda t: t.due_on)


def get_upcoming_tasks(days: int = 7, workspace_gid: str = "") -> list[Task]:
    """Get tasks due in the next N days."""
    api_client = get_api_client()

    if not workspace_gid:
        workspace_gid = _get_workspace_gid(api_client)

    tasks_api = asana.TasksApi(api_client)
    today = date.today().isoformat()
    future = (date.today() + timedelta(days=days)).isoformat()

    try:
        result = tasks_api.search_tasks_for_workspace(
            workspace_gid=workspace_gid,
            opts={
                "due_on.after": today,
                "due_on.before": future,
                "completed": False,
                "sort_by": "due_date",
                "sort_ascending": True,
                "opt_fields": "name,completed,due_on,due_at,assignee.name,memberships.project.name",
            },
        )
        return [_parse_task(t) for t in result]

    except ApiException as e:
        if e.status == 402:
            return _upcoming_fallback(api_client, workspace_gid, today, future)
        raise


def _upcoming_fallback(api_client: asana.ApiClient, workspace_gid: str, today: str, future: str) -> list[Task]:
    """Fallback for free-tier: get my incomplete tasks and filter client-side."""
    tasks_api = asana.TasksApi(api_client)
    users_api = asana.UsersApi(api_client)
    me = users_api.get_user("me", opts={})

    result = tasks_api.get_tasks(opts={
        "assignee": me["gid"],
        "workspace": workspace_gid,
        "completed_since": "now",
        "opt_fields": "name,completed,due_on,due_at,assignee.name,memberships.project.name",
    })

    upcoming = []
    for t in result:
        task = _parse_task(t)
        if not task.completed and task.due_on and today <= task.due_on <= future:
            upcoming.append(task)

    return sorted(upcoming, key=lambda t: t.due_on)


def list_projects(workspace_gid: str = "") -> list[Project]:
    """List projects in the workspace."""
    api_client = get_api_client()

    if not workspace_gid:
        workspace_gid = _get_workspace_gid(api_client)

    projects_api = asana.ProjectsApi(api_client)
    result = projects_api.get_projects(opts={
        "workspace": workspace_gid,
        "opt_fields": "name,due_on,owner.name",
    })

    projects = []
    for p in result:
        owner = ""
        if p.get("owner"):
            owner = p["owner"].get("name", "")
        projects.append(Project(
            gid=p["gid"],
            name=p.get("name", ""),
            owner=owner,
            due_on=p.get("due_on", "") or "",
        ))

    return projects


def format_task_list(tasks: list[Task], title: str = "Tasks") -> str:
    """Format task list for display."""
    if not tasks:
        return f"No {title.lower()} found."

    lines = [f"{title}:", ""]
    for t in tasks:
        status = "[x]" if t.completed else "[ ]"
        due = f"Due: {t.due_on}" if t.due_on else "No due date"
        assignee = f"  Assignee: {t.assignee}" if t.assignee else ""
        project = f"  Project: {t.project}" if t.project else ""

        lines.append(f"{status} {t.name}  ({due}){assignee}{project}")
        lines.append(f"    GID: {t.gid}")
        lines.append("")

    return "\n".join(lines)


def format_project_list(projects: list[Project]) -> str:
    """Format project list for display."""
    if not projects:
        return "No projects found."

    lines = ["Projects:", ""]
    for p in projects:
        owner = f"  Owner: {p.owner}" if p.owner else ""
        due = f"  Due: {p.due_on}" if p.due_on else ""
        lines.append(f"  {p.name}  (GID: {p.gid}){owner}{due}")

    return "\n".join(lines)
