---
name: vault-structure
description: Teaches the agent how to organize files in the memory vault
autoTrigger: true
---

# Vault Structure

Use this skill whenever you need to save, retrieve, or organize information in the memory vault.

## Vault Location

`Dynamous/Memory/`

## Folder Layout and Naming Conventions

| Folder | What goes here | Naming pattern |
|--------|---------------|----------------|
| `daily/` | Append-only timestamped logs | `YYYY-MM-DD.md` |
| `meetings/` | Meeting notes and decisions | `YYYY-MM-DD-<topic-slug>.md` |
| `projects/` | Project status and progress | `<project-name>.md` |
| `clients/` | Client/customer information | `<client-name>.md` |
| `research/` | Research and learning notes | `<topic-slug>.md` |
| `content/` | Content ideas and drafts | `<title-slug>.md` |
| `team/` | Team member context | `<person-name>.md` |
| `drafts/active/` | Auto-generated reply drafts | `YYYY-MM-DD_<type>_<slug>.md` |
| `drafts/sent/` | Captured real replies (for RAG) | `YYYY-MM-DD_<type>_<slug>.md` |
| `drafts/expired/` | Drafts older than 24h, no reply | `YYYY-MM-DD_<type>_<slug>.md` |

## Root Files

| File | Purpose | Loaded into context? |
|------|---------|---------------------|
| `SOUL.md` | Agent personality and rules | Yes (every session) |
| `USER.md` | Vidit's profile, accounts, team | Yes (every session) |
| `MEMORY.md` | Long-term knowledge (concise!) | Yes (every session) |
| `HEARTBEAT.md` | What the heartbeat monitors | No (heartbeat only) |
| `HABITS.md` | Daily improvement pillars | Yes (every session) |

## Rules

1. **Daily log is append-only.** Never edit past entries. Always add with a `- **HH:MM** —` timestamp prefix.
2. **MEMORY.md must stay concise** (<500 lines). It loads into every conversation. Only promote truly important items here.
3. **Use slugified names** for files: lowercase, hyphens instead of spaces, no special characters. Example: `2026-04-13-api-design-review.md`
4. **One entity per file** in `clients/`, `team/`, and `projects/`. Don't merge multiple clients into one file.
5. **Drafts follow the lifecycle:** `active/` → `sent/` (when real reply detected) or `expired/` (after 24h).
6. **Always check if a file exists** before creating a new one. Update existing files rather than duplicating.
7. **Meeting notes go to `meetings/`**, not the daily log. The daily log gets a one-line reference: `- **14:00** — Meeting notes saved to meetings/2026-04-13-sprint-planning.md`
