#!/usr/bin/env python3
"""Claude Code SessionStart hook.

Tells Claude where each SDLC workspace (docs/sdlc/<slug>/STATUS.md) stands, so
a new, cleared, resumed or compacted session continues the right work instead
of re-reading everything. It prints the current phase, the next open item of
the current phase plan and the "## Handoff" section, which the android-sdlc
skill rewrites at the end of every session. Stdout becomes session context.

Install at: .claude/hooks/session-context.py   (chmod +x)
"""
import json
import os
import re
import sys
from pathlib import Path

HANDOFF_MAX_LINES = 30
HANDOFF_MAX_CHARS = 3000
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
SECTION = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def cells(row):
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def sections(text):
    """Maps each "## " heading to the text under it, up to the next "## " heading."""
    matches = list(SECTION.finditer(text))
    return {
        m.group(1): text[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(text)]
        for i, m in enumerate(matches)
    }


def field(text, name):
    """The value of a "| Field | Value |" row in the header table, or ''."""
    for line in text.splitlines():
        if line.lstrip().startswith("|"):
            row = cells(line)
            if len(row) >= 2 and row[0].lower() == name.lower():
                return row[1]
    return ""


def next_plan_item(text):
    """The first row of the newest "## Phase N plan" whose status isn't Done, as "#: PR", or ''."""
    plans = [(heading, body) for heading, body in sections(text).items() if re.fullmatch(r"Phase \d+ plan", heading)]
    if not plans:
        return ""
    heading, body = max(plans, key=lambda plan: int(re.search(r"\d+", plan[0]).group()))
    rows = [cells(line) for line in body.splitlines() if line.lstrip().startswith("|")]
    for row in rows[2:]:  # skip the header and the separator
        if len(row) >= 2 and not row[-1].lower().startswith("done"):
            return f"{heading} #{row[0]}: {row[1]} ({row[-1]})"
    return ""


def handoff(text):
    """The "## Handoff" section without comments or blank lines, capped, or ''."""
    body = sections(text).get("Handoff", "")
    lines = [line for line in COMMENT.sub("", body).splitlines() if line.strip()]
    capped = "\n".join(lines[:HANDOFF_MAX_LINES])
    truncated = len(lines) > HANDOFF_MAX_LINES or len(capped) > HANDOFF_MAX_CHARS
    return capped[:HANDOFF_MAX_CHARS] + ("\n… (truncated: keep the Handoff section short)" if truncated else "")


def describe(project_dir, status_file):
    text = status_file.read_text(encoding="utf-8")
    lines = [f"SDLC workspace {status_file.parent.relative_to(project_dir)}/ (read STATUS.md for the detail):"]
    for name in ("Current phase", "Code review mode", "Last updated"):
        value = field(text, name)
        if value:
            lines.append(f"- {name}: {value}")
    item = next_plan_item(text)
    if item:
        lines.append(f"- Next plan item: {item}")
    note = handoff(text)
    if note:
        lines += [
            "",
            'Handoff from the last session (STATUS.md "## Handoff"). Start from its next action, load only '
            "what it lists, and rewrite it before this session ends (CLAUDE.md, Sessions and gates):",
            note,
        ]
    return "\n".join(lines)


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())
    status_files = sorted(project_dir.glob("docs/sdlc/*/STATUS.md"))
    if not status_files:
        return 0
    blocks = [describe(project_dir, status_file) for status_file in status_files]
    if os.environ.get("SDLC_GATE", "").lower() == "off":
        blocks.append(
            "SDLC_GATE=off: the user has switched off the baseline gate for this session. Baselined documents "
            "still change only through an approved CR; say so when you edit one."
        )
    print("\n\n".join(blocks))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:  # never wedge a session on a hook bug
        print(f"session-context hook error (ignored): {error}", file=sys.stderr)
        sys.exit(0)
