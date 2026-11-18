#!/usr/bin/env python3
"""Claude Code PreToolUse hook (Edit|Write|MultiEdit).

Blocks new production Kotlin that breaks the project's coding and
architecture rules (.claude/rules/, the mobile-android-sdlc, mobile-multiplatform-sdlc
and ktor-sdlc code patterns). Production code is src/main/ and the Kotlin
Multiplatform source sets (src/commonMain/, src/androidMain/, src/iosMain/, ...).
Only the text being written is checked, so existing legacy code is never
flagged. Exit code 2 stops the tool call and shows stderr to Claude.

Install at: .claude/hooks/guard-kotlin-rules.py   (chmod +x)
"""
import json
import re
import sys

RULES_HINT = (
    ".claude/rules/ and the code-patterns.md of .claude/skills/mobile-android-sdlc, "
    ".claude/skills/mobile-multiplatform-sdlc or .claude/skills/ktor-sdlc"
)
COMMENT_PREFIXES = ("//", "/*", "*")
PRODUCTION_SOURCE = re.compile(r"/src/(main|\w+Main)/")
DI_MODULE = re.compile(r"@Provides|\bmodule\s*\{")


def everywhere(path, text):
    return True


def in_domain_layer(path, text):
    return "/domain/" in path or "/core/model/" in path


def in_view_model(path, text):
    return path.endswith("ViewModel.kt")


def in_route_file(path, text):
    """Ktor route files: routes call services, never repositories or Exposed."""
    return path.endswith(("Routes.kt", "Routing.kt")) or "/routes/" in path


def outside_di_module(path, text):
    """True unless the text is a Hilt module (@Provides) or a Koin module (module { ... })."""
    return not DI_MODULE.search(text)


# (pattern, rule, applies_to)
CHECKS = [
    (r"[\w)\]]!!", "No `!!`: use `?.`, `?:` or `requireNotNull(x) { \"reason\" }`.", everywhere),
    (
        r"\bGlobalScope\b",
        "No `GlobalScope`: use viewModelScope, a suspend function or WorkManager "
        "(`application.launch` or a queue in a Ktor service).",
        everywhere,
    ),
    (r"\brunBlocking\b", "No `runBlocking` in production code.", everywhere),
    (
        r"\bprintln\(|\.printStackTrace\(\)|\bThread\.sleep\(",
        "No `println`, `printStackTrace()` or `Thread.sleep` in production code: "
        "use the project's logger (SLF4J, Timber, Kermit) and `delay`.",
        everywhere,
    ),
    (
        r"\bText\(\s*(text\s*=\s*)?\"",
        "No hard-coded UI text: use `stringResource(R.string.…)`, or `stringResource(Res.string.…)` in Compose Multiplatform.",
        everywhere,
    ),
    (
        r"\bDispatchers\.(IO|Default)\b",
        "Inject dispatchers (`@IoDispatcher`/`@DefaultDispatcher`, or `AppDispatchers` in Kotlin Multiplatform "
        "and Ktor services) instead of hard-coding them.",
        outside_di_module,
    ),
    (
        r"^\s*import\s+(android|androidx|retrofit2|okhttp3|dagger\.hilt\.android|io\.ktor|platform"
        r"|org\.jetbrains\.exposed|java\.sql|javax\.sql|com\.zaxxer\.hikari|org\.flywaydb)\.",
        "The domain layer is pure Kotlin: no Android, iOS (`platform.*`), Retrofit, OkHttp, Ktor, Hilt-Android, "
        "Exposed, JDBC, HikariCP or Flyway imports.",
        in_domain_layer,
    ),
    (r"\b[A-Z]\w*Repository(Impl)?\b", "ViewModels call UseCases, never repositories.", in_view_model),
    (
        r"\b[A-Z]\w*Repository(Impl)?\b|^\s*import\s+org\.jetbrains\.exposed\.",
        "Routes call services; database access lives in the persistence adapter.",
        in_route_file,
    ),
]


def read_tool_call():
    """Returns the target path and the new text: Write content, Edit new_string or MultiEdit edits."""
    tool_input = json.load(sys.stdin).get("tool_input", {})
    parts = [tool_input.get("content", ""), tool_input.get("new_string", "")]
    parts += [edit.get("new_string", "") for edit in tool_input.get("edits", [])]
    return tool_input.get("file_path", ""), "\n".join(parts)


def find_violations(path, text):
    code_lines = [line for line in text.splitlines() if not line.strip().startswith(COMMENT_PREFIXES)]
    violations = []
    for pattern, rule, applies_to in CHECKS:
        if not applies_to(path, text):
            continue
        hits = [line.strip() for line in code_lines if re.search(pattern, line)]
        if hits:
            violations.append((rule, hits))
    return violations


def main():
    try:
        path, text = read_tool_call()
    except ValueError:
        return 0
    if not (path.endswith(".kt") and PRODUCTION_SOURCE.search(path)):
        return 0

    violations = find_violations(path, text)
    if not violations:
        return 0

    print(f"Blocked by guard-kotlin-rules hook: {path}", file=sys.stderr)
    for rule, hits in violations:
        print(f"- {rule}", file=sys.stderr)
        for hit in hits:
            print(f"    {hit}", file=sys.stderr)
    print(f"Fix the new code and try again. Rules: {RULES_HINT}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
