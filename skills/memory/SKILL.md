---
name: memory
description: Control Second Brain memory level — full, light, or off
argument-hint: "{full|light|off|status}"
triggers:
  - "memory level"
  - "change memory"
  - "disable memory"
  - "enable memory"
  - "memory settings"
  - "memory status"
---

# Memory Control

Change how much memory the Second Brain uses per session.

## Usage

- `/second-brain:memory status` — Show current memory level
- `/second-brain:memory full` — Enable all memory features (highest token usage)
- `/second-brain:memory light` — Memory loading only, no auto-logging (low token usage)
- `/second-brain:memory off` — Disable all memory hooks (zero extra tokens)

## Memory Levels

| Level | SessionStart (load memory) | Stop hook (auto-log + CLI) | PreCompact/SessionEnd (save context) | Guardrails | Extra tokens per response |
|-------|---------------------------|---------------------------|--------------------------------------|-----------|--------------------------|
| **full** | Yes | Yes (Claude CLI call) | Yes | Yes | ~500-1000 |
| **light** | Yes | No | Yes | Yes | ~200-400 |
| **off** | No | No | No | Yes (always on) | 0 |

## Workflow

### For `status` (or no argument):
Read `~/.second-brain/config.json` and show the current `memory_level` value with explanation.

### For `full`, `light`, or `off`:
1. Read `~/.second-brain/config.json`
2. Update `memory_level` to the requested value
3. Write back to `~/.second-brain/config.json`
4. Tell the user what changed and what it means:
   - **full**: "Memory fully enabled. Decisions, action items, and new entities will be auto-detected and saved after every response. This uses ~500-1000 extra tokens per response."
   - **light**: "Memory set to light mode. Your vault context loads at session start and saves on exit, but the Stop hook (auto-logging) is disabled. This saves ~300-600 tokens per response."
   - **off**: "Memory disabled. Only security guardrails remain active. No vault loading, no auto-logging. To re-enable: `/second-brain:memory full`"
5. Tell the user: "Changes take effect in your next session."
