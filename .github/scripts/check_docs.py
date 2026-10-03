"""Repository documentation check, version 1.1 (Python standard library only).

Maintained with the repository procedure templates. Run from repository root.
PR text is data: never execute it. This checks structure, not the author's judgment.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROLES = ("requirements", "decisions", "known-issues", "progress")


def validate_documents(root):
    config = json.loads((root / ".github/repository-docs.json").read_text(encoding="utf-8"))
    if set(config["documents"]) != set(ROLES):
        raise ValueError("Map exactly the four documentation roles.")
    seen = set()
    for role, relative in config["documents"].items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()) or path in seen:
            raise ValueError("Document paths must be distinct and inside the repository.")
        seen.add(path)
        content = path.read_text(encoding="utf-8")
        if not content.startswith("# ") or "> Purpose:" not in content or "**Status:**" not in content:
            raise ValueError(f"{relative}: add a title, purpose and status.")
    return config


def validate_impact(body, changed):
    # Ignore the template's instructional comments, including multiline comments.
    body = re.sub(r"<!--.*?-->", "", body or "", flags=re.S)
    modes = re.findall(r"^Documentation impact:[ \t]*(.*?)[ \t]*\r?$", body, flags=re.M)
    details = re.findall(r"^Documentation details:[ \t]*(.*?)[ \t]*\r?$", body, flags=re.M)
    if len(modes) != 1 or modes[0] not in ("updated", "none") or len(details) != 1:
        raise ValueError("Use exactly one 'Documentation impact: updated|none' and 'Documentation details: <explanation>' line.")
    detail = details[0]
    if len(detail) < 20 or re.search(r"\b(TODO|TBD|placeholder)\b|<[^>]+>|\[explanation\]", detail, re.I):
        raise ValueError("Documentation details must contain a specific explanation, not a placeholder.")
    if modes[0] == "updated":
        docs = [p for p in changed if p.endswith(".md") and "pull_request_template" not in p.lower()]
        if not any(p in detail for p in docs):
            raise ValueError("For 'updated', name at least one changed Markdown path in Documentation details.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", type=Path, help="GitHub pull_request event JSON; omit for local structure check")
    args = parser.parse_args()
    root = Path.cwd()
    try:
        validate_documents(root)
        if args.event:
            event = json.loads(args.event.read_text(encoding="utf-8"))
            pr = event["pull_request"]
            base, head = pr["base"]["sha"], pr["head"]["sha"]
            if not all(re.fullmatch(r"[0-9a-f]{40}", value) for value in (base, head)):
                raise ValueError("Expected full Git commit SHAs in the event.")
            changed = subprocess.check_output(
                ["git", "diff", "--name-only", "--diff-filter=ACMR", "-z", f"{base}...{head}", "--"],
            ).decode("utf-8").split("\0")
            validate_impact(pr.get("body"), changed)
        print("Documentation assessment passed. Reviewer must verify accuracy and completeness.")
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Documentation assessment failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
