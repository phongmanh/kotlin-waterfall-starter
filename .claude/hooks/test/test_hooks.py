"""Tests for the SDLC hooks. Run from the repo root: python3 -m unittest discover -s .claude/hooks/test"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOKS = Path(__file__).resolve().parent.parent

STATUS = """# STATUS: Demo

| Field | Value |
|---|---|
| Current phase | 4 Implementation: in progress |
| Last updated | 2026-11-10 |

## Deliverables
| Phase | Deliverable | File | Status (Not started / Draft / In review / Approved) | Version |
|---|---|---|---|---|
| 1 | Requirements | requirements.md | Approved | 1.0 |

## Phase 3 plan
| # | Work | Covers | Needs from the owner | Status |
|---|---|---|---|---|
| 1 | Old design | FR-001 | — | Not started |

## Phase 4 plan
| # | PR | Covers | Needs from the owner | Status |
|---|---|---|---|---|
| 1 | Skeleton | ADR-0002 | — | Done 2026-10-23 |
| 2 | Domain | NFR-COMPAT-02 | — | Not started |
"""

HANDOFF = """
## Handoff
<!-- guidance -->
- **Next action:** plan PR 2
- **Load:** design/app-shell.md §5
"""


def run_hook(name, project, payload, **env):
    return subprocess.run(
        [sys.executable, str(HOOKS / name)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(project), "SDLC_GATE": "", **env},
        check=True,
    )


class ProjectTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name)
        self.workspace = self.project / "docs/sdlc/demo"
        self.workspace.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write_status(self, text):
        (self.workspace / "STATUS.md").write_text(text, encoding="utf-8")


class SessionContextTest(ProjectTestCase):
    def test_reports_phase_and_next_item_of_the_newest_plan(self):
        self.write_status(STATUS)
        out = run_hook("session-context.py", self.project, {"source": "clear"}).stdout
        self.assertIn("docs/sdlc/demo/", out)
        self.assertIn("Current phase: 4 Implementation: in progress", out)
        self.assertIn("Next plan item: Phase 4 plan #2: Domain (Not started)", out)
        self.assertNotIn("Handoff", out)

    def test_injects_the_handoff_without_comments(self):
        self.write_status(STATUS + HANDOFF)
        out = run_hook("session-context.py", self.project, {"source": "clear"}).stdout
        self.assertIn("Handoff from the last session", out)
        self.assertIn("- **Next action:** plan PR 2", out)
        self.assertNotIn("guidance", out)

    def test_caps_a_long_handoff(self):
        long = "\n## Handoff\n" + "\n".join(f"- line {i}" for i in range(50)) + "\n"
        self.write_status(STATUS + long)
        out = run_hook("session-context.py", self.project, {}).stdout
        self.assertIn("- line 29", out)
        self.assertNotIn("- line 30", out)
        self.assertIn("truncated", out)

    def test_says_when_the_gate_is_off(self):
        self.write_status(STATUS)
        out = run_hook("session-context.py", self.project, {}, SDLC_GATE="off").stdout
        self.assertIn("SDLC_GATE=off", out)

    def test_prints_nothing_without_a_workspace(self):
        (self.workspace / "STATUS.md").unlink(missing_ok=True)
        self.assertEqual(run_hook("session-context.py", self.project, {}).stdout, "")


class BaselineGuardTest(ProjectTestCase):
    def edit(self, relative_path, **env):
        payload = {"tool_name": "Edit", "tool_input": {"file_path": str(self.workspace / relative_path)}}
        return run_hook("guard-sdlc-baseline.py", self.project, payload, **env).stdout

    def test_asks_before_editing_a_baselined_document(self):
        self.write_status(STATUS)
        decision = json.loads(self.edit("requirements.md"))["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "ask")
        self.assertIn("SDLC_GATE=off", decision["permissionDecisionReason"])

    def test_lets_living_files_through(self):
        self.write_status(STATUS)
        self.assertEqual(self.edit("STATUS.md"), "")

    def test_gate_off_lets_baselined_documents_through(self):
        self.write_status(STATUS)
        self.assertEqual(self.edit("requirements.md", SDLC_GATE="OFF"), "")


if __name__ == "__main__":
    unittest.main()
