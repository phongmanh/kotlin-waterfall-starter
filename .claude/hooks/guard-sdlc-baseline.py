#!/usr/bin/env python3
"""Claude Code PreToolUse hook (Edit|Write|MultiEdit).

Keeps the phase gates of the SDLC skills (android-sdlc,
compose-multiplatform-sdlc, ktor-sdlc) real. Before Claude edits a deliverable
under docs/sdlc/<slug>/ that STATUS.md marks as Approved (baselined), the user
is asked to confirm. A baselined document should change only through an
approved change request (cr/CR-NNN-*.md). STATUS.md, rtm.md and cr/ are
living files and are never gated.

The user (never Claude) can switch the gate off by setting SDLC_GATE=off,
e.g. in the git-ignored .claude/settings.local.json:
    { "env": { "SDLC_GATE": "off" } }

Install at: .claude/hooks/guard-sdlc-baseline.py   (chmod +x)
"""
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

LIVING_FILES = {"STATUS.md", "rtm.md"}
DELIVERABLES_HEADING = "## Deliverables"


def cells(row):
    return [cell.strip().strip("`") for cell in row.strip().strip("|").split("|")]


def as_glob(file_cell):
    """Turns template placeholders such as design/<feature>.md or adr/NNNN-<decision>.md into a glob."""
    return re.sub(r"<[^>]*>|NNNN", "*", file_cell)


def is_approved(status_text, relative_path):
    """True if the Deliverables table in STATUS.md lists relative_path with status Approved."""
    in_section, file_col, status_col = False, None, None
    for line in status_text.splitlines():
        if line.startswith("#"):
            in_section = line.strip() == DELIVERABLES_HEADING
            continue
        if not in_section or not line.lstrip().startswith("|"):
            continue
        row = cells(line)
        if file_col is None:
            if "File" in row and any(cell.startswith("Status") for cell in row):
                file_col = row.index("File")
                status_col = next(i for i, cell in enumerate(row) if cell.startswith("Status"))
            continue
        if len(row) <= max(file_col, status_col):
            continue
        if fnmatch.fnmatch(relative_path, as_glob(row[file_col])) and row[status_col].lower().startswith("approved"):
            return True
    return False


def main():
    if os.environ.get("SDLC_GATE", "").lower() == "off":
        return 0
    try:
        path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
    except ValueError:
        return 0
    match = re.search(r"^(.*/docs/sdlc/[^/]+)/(.+)$", path)
    if not match:
        return 0

    workspace, relative_path = Path(match.group(1)), match.group(2)
    if relative_path in LIVING_FILES or relative_path.startswith("cr/"):
        return 0
    status_file = workspace / "STATUS.md"
    if not status_file.is_file() or not is_approved(status_file.read_text(encoding="utf-8"), relative_path):
        return 0

    reason = (
        f"{relative_path} is baselined (Approved in STATUS.md). Change it only through an approved "
        "change request (cr/CR-NNN-*.md), or confirm that this is a non-substantive fix. Only the user "
        "may switch this gate off (SDLC_GATE=off in .claude/settings.local.json); don't edit STATUS.md, "
        "the hooks or the settings to get past it."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
