#!/usr/bin/env python3
"""Utility to append a new release section into changelog.md."""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate changelog entry skeleton.")
    parser.add_argument("--changelog", default="changelog.md", help="Path to changelog file.")
    parser.add_argument("--version-file", default="version", help="Path to file that stores new version.")
    parser.add_argument("--new-version", help="Override new version instead of reading version file.")
    parser.add_argument("--previous-version", help="Override previous version instead of reading changelog.")
    parser.add_argument("--hotfix", action="store_true", help="Mark entry as hotfix.")
    parser.add_argument(
        "--branches",
        nargs="*",
        default=None,
        help="List branches included in release.",
    )
    parser.add_argument(
        "--exclude-branches",
        nargs="*",
        default=None,
        help="Branch names to exclude when auto-discovering branches.",
    )
    parser.add_argument(
        "--date",
        help="Date to use in entry (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--description-placeholder",
        default="- [ ] Добавьте описание изменений вручную",
        help="Placeholder line for manual description.",
    )
    parser.add_argument(
        "--description-file",
        default="scripts/changelog/description.txt",
        help="Path to file with manual description text.",
    )
    parser.add_argument(
        "--clear-description-file",
        action="store_true",
        help="Truncate description file after successful generation.",
    )
    return parser.parse_args()


def read_version(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise SystemExit(f"version file not found: {path}") from exc
    if not text:
        raise SystemExit(f"version file {path} is empty")
    return text


def detect_previous_version(path: Path) -> str | None:
    if not path.exists():
        return None
    pattern = re.compile(r"(\d+\.\d+\.\d+)")
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("##"):
            continue
        match = pattern.search(line)
        if match:
            return match.group(1)
    return None


def build_entry(
    new_version: str,
    previous_version: str | None,
    release_date: str,
    branches: list[str],
    description: str,
    is_hotfix: bool,
) -> str:
    label = "Hotfix " if is_hotfix else ""
    baseline = previous_version or "N/A"
    header = f"## {label}{new_version} ({baseline} -> {new_version}) - {release_date}"
    branch_lines = "\n".join(f"- {branch}" for branch in branches) if branches else "- [ ] Добавьте ветки, вошедшие в релиз"
    return (
        f"{header}\n\n"
        f"### Ветки\n"
        f"{branch_lines}\n\n"
        f"### Описание\n"
        f"{description}\n"
    )


def inject_entry(changelog_text: str, entry: str) -> str:
    lines = changelog_text.splitlines()
    if lines:
        header = lines[0]
        if header.strip().lower().startswith("# changelog"):
            rest = "\n".join(lines[1:]).lstrip("\n")
            suffix = f"\n{rest}" if rest else ""
            return f"{header}\n\n{entry}{suffix}"
    trimmed = changelog_text.lstrip("\n")
    prefix = "" if trimmed else "# Changelog\n\n"
    return f"{prefix}{entry}{trimmed}"


def discover_branches(exclude: set[str]) -> list[str]:
    """Return repository branches excluding specified ones and special refs."""
    commands = [
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/"],
        ["git", "branch", "--format=%(refname:short)"],
    ]
    seen: list[str] = []
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError:
            continue
        for raw in result.stdout.splitlines():
            name = raw.strip()
            if not name:
                continue
            if name.startswith("origin/"):
                name = name.split("/", 1)[1]
            if name.startswith("remotes/"):
                name = name.split("/", 1)[1]
            if name in exclude or name in ("HEAD",):
                continue
            if name not in seen:
                seen.append(name)
    return seen


def main() -> None:
    args = parse_args()
    changelog_path = Path(args.changelog)
    new_version = args.new_version or read_version(Path(args.version_file))
    previous_version = args.previous_version or detect_previous_version(changelog_path)
    release_date = args.date or dt.date.today().isoformat()
    exclude = {"main", "prod"}
    if args.exclude_branches:
        exclude.update(args.exclude_branches)
    if args.branches is not None:
        branches = [branch for branch in args.branches if branch not in exclude]
    else:
        branches = discover_branches(exclude)
    description_file = Path(args.description_file)
    if description_file.exists():
        description_text = description_file.read_text(encoding="utf-8").strip()
    else:
        description_text = ""
    if not description_text:
        raise SystemExit(
            "Description file is empty. "
            "Add release notes to scripts/changelog/description.txt before generating changelog.",
        )
    entry = build_entry(
        new_version=new_version,
        previous_version=previous_version,
        release_date=release_date,
        branches=branches,
        description=description_text,
        is_hotfix=args.hotfix,
    )
    changelog_text = changelog_path.read_text(encoding="utf-8") if changelog_path.exists() else "# Changelog\n"
    changelog_path.write_text(inject_entry(changelog_text, entry), encoding="utf-8")
    if args.clear_description_file and description_file.exists():
        description_file.write_text("", encoding="utf-8")
    print(f"Changelog updated with {new_version} entry.")


if __name__ == "__main__":
    main()
