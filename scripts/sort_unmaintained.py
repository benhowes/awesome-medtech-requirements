#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.31.0",
# ]
# ///
"""Move unmaintained GitHub-hosted entries into a collapsed block per section.

For every list entry whose main link points at a GitHub repository, look up the
repository and decide whether it is unmaintained: archived, or no commits on the
default branch for --stale-years years. Unmaintained entries are moved into a
collapsed <details> block at the end of their section (newest first) and
annotated with the year of their last commit. Entries that become active again
are moved back to the end of the main list.

Entries whose main link is a docs site rather than GitHub can name their
repository with an invisible hint on the first line:

    - **[Tool](https://tool.example.com/)** <!-- github: owner/repo -->

Entries with neither are never moved, so they can be placed in (or out of) the
collapsed block by hand.

Usage:
    uv run scripts/sort_unmaintained.py              # rewrite README.md
    uv run scripts/sort_unmaintained.py --check      # exit 1 if changes are needed

Set GITHUB_TOKEN to avoid the unauthenticated API rate limit.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

API = "https://api.github.com"
SUMMARY = "<summary>Unmaintained (archived, or no commits in {years}+ years)</summary>"

ENTRY_RE = re.compile(r"^- ")
CONTINUATION_RE = re.compile(r"^  +\S")
GITHUB_RE = re.compile(
    r"\]\(https?://(?:www\.)?github\.com/([\w.-]+)/([\w.-]+?)(?:\.git)?/?(?:[#?][^)]*)?\)"
)
HINT_RE = re.compile(r"<!--\s*github:\s*([\w.-]+)/([\w.-]+)\s*-->")
NOTE_RE = re.compile(r" _\((?:archived|last commit)[^)]*\)_$")
# github.com paths that look like owner/repo but are not repositories
NON_REPO_OWNERS = {"topics", "orgs", "apps", "marketplace", "sponsors", "features", "collections"}


@dataclass
class RepoStatus:
    archived: bool
    last_commit: datetime | None

    def is_stale(self, now: datetime, years: float) -> bool:
        if self.archived:
            return True
        return self.last_commit is not None and now - self.last_commit > timedelta(days=365 * years)

    def note(self) -> str:
        parts = ["archived"] if self.archived else []
        if self.last_commit is not None:
            parts.append(f"last commit {self.last_commit.year}")
        return f" _({', '.join(parts)})_"


@dataclass
class Entry:
    lines: list[str]

    @property
    def repo(self) -> str | None:
        match = HINT_RE.search(self.lines[0]) or GITHUB_RE.search(self.lines[0])
        if not match or match.group(1).lower() in NON_REPO_OWNERS:
            return None
        return f"{match.group(1)}/{match.group(2)}"

    def with_note(self, note: str) -> Entry:
        first = NOTE_RE.sub("", self.lines[0]) + note
        return Entry([first, *self.lines[1:]])


@dataclass
class Section:
    head: list[str]
    active: list[Entry] = field(default_factory=list)
    stale: list[Entry] = field(default_factory=list)
    rest: list[str] = field(default_factory=list)

    def render(self, years: float) -> list[str]:
        out = list(self.head)
        for entry in self.active:
            out += entry.lines
        if self.stale:
            if self.active:
                out.append("")
            out += ["<details>", SUMMARY.format(years=_fmt_years(years)), ""]
            for entry in self.stale:
                out += entry.lines
            out += ["", "</details>"]
        return out + self.rest


def _fmt_years(years: float) -> str:
    return str(int(years)) if float(years).is_integer() else str(years)


def parse_section(lines: list[str]) -> Section:
    """Split a section into intro, active list, collapsed list and trailing lines."""
    section = Section(head=[])
    i = 0
    while i < len(lines) and not ENTRY_RE.match(lines[i]) and lines[i].strip() != "<details>":
        section.head.append(lines[i])
        i += 1

    target = section.active
    in_details = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if ENTRY_RE.match(line):
            target.append(Entry([line]))
        elif CONTINUATION_RE.match(line) and target:
            target[-1].lines.append(line)
        elif stripped == "<details>" and not in_details:
            in_details, target = True, section.stale
        elif in_details and stripped.startswith("<summary>"):
            pass
        elif in_details and stripped == "</details>":
            in_details = False
            i += 1
            break
        elif stripped == "":
            # Blank lines inside the list area are regenerated on render. Keep
            # the ones that end the list (unless a <details> block follows).
            if not in_details:
                j = i
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                if j >= len(lines) or lines[j].strip() != "<details>":
                    break
        else:
            break
        i += 1

    if in_details:
        raise ValueError("unterminated <details> block")
    section.rest = lines[i:]
    return section


def split_sections(text: str) -> list[list[str]]:
    """Split markdown into chunks that each start at a level-2 heading."""
    chunks: list[list[str]] = [[]]
    for line in text.split("\n"):
        if line.startswith("## "):
            chunks.append([])
        chunks[-1].append(line)
    return chunks


def rearrange(
    text: str,
    statuses: dict[str, RepoStatus | None],
    now: datetime,
    years: float,
) -> tuple[str, list[str]]:
    """Return the rearranged markdown and a list of human-readable changes."""
    chunks = split_sections(text)
    out = chunks[0]
    changes: list[str] = []

    for chunk in chunks[1:]:
        heading, section = chunk[0], parse_section(chunk[1:])
        name = heading.removeprefix("## ").strip()
        active: list[Entry] = []
        stale: list[tuple[Entry, RepoStatus | None]] = []

        for entry, was_stale in [(e, False) for e in section.active] + [(e, True) for e in section.stale]:
            status = statuses.get(entry.repo) if entry.repo else None
            if status is None:
                # Unknown or not on GitHub: leave it where it is.
                if was_stale:
                    stale.append((entry, None))
                else:
                    active.append(entry)
                continue
            if status.is_stale(now, years):
                stale.append((entry.with_note(status.note()), status))
                if not was_stale:
                    changes.append(f"{name}: moved `{entry.repo}` to unmaintained ({status.note().strip(' _()')})")
            else:
                active.append(entry.with_note(""))
                if was_stale:
                    changes.append(f"{name}: moved `{entry.repo}` back to active")

        epoch = datetime.min.replace(tzinfo=timezone.utc)
        stale.sort(
            key=lambda pair: pair[1].last_commit or epoch if pair[1] else epoch,
            reverse=True,
        )
        section.active = active
        section.stale = [entry for entry, _ in stale]
        out += [heading, *section.render(years)]

    return "\n".join(out), changes


def repos_in(text: str) -> list[str]:
    repos: list[str] = []
    for chunk in split_sections(text)[1:]:
        section = parse_section(chunk[1:])
        for entry in section.active + section.stale:
            if entry.repo and entry.repo not in repos:
                repos.append(entry.repo)
    return repos


def fetch_status(session: requests.Session, repo: str) -> RepoStatus | None:
    response = session.get(f"{API}/repos/{repo}", timeout=20)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    info = response.json()

    commits = session.get(
        f"{API}/repos/{info['full_name']}/commits",
        params={"per_page": 1, "sha": info["default_branch"]},
        timeout=20,
    )
    last_commit = None
    if commits.status_code != 409:  # 409: empty repository
        commits.raise_for_status()
        data = commits.json()
        if data:
            last_commit = datetime.fromisoformat(data[0]["commit"]["committer"]["date"].replace("Z", "+00:00"))
    return RepoStatus(archived=info["archived"], last_commit=last_commit)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("readme", nargs="?", default="README.md", type=Path)
    parser.add_argument("--stale-years", type=float, default=2, help="years without commits before a repo is unmaintained")
    parser.add_argument("--check", action="store_true", help="don't write; exit 1 if the file would change")
    parser.add_argument("--summary", type=Path, help="write a markdown summary of changes to this file")
    args = parser.parse_args()

    text = args.readme.read_text(encoding="utf-8")
    session = requests.Session()
    session.headers["Accept"] = "application/vnd.github+json"
    if token := os.environ.get("GITHUB_TOKEN"):
        session.headers["Authorization"] = f"Bearer {token}"

    statuses: dict[str, RepoStatus | None] = {}
    for repo in repos_in(text):
        try:
            statuses[repo] = fetch_status(session, repo)
        except requests.RequestException as exc:
            print(f"warning: could not check {repo}: {exc}", file=sys.stderr)
            statuses[repo] = None
            continue
        status = statuses[repo]
        label = "not found" if status is None else status.note().strip(" _()") or "no commits"
        print(f"{repo}: {label}")

    new_text, changes = rearrange(text, statuses, datetime.now(timezone.utc), args.stale_years)

    if args.summary:
        body = "\n".join(f"- {c}" for c in changes) or "No changes."
        args.summary.write_text(body + "\n", encoding="utf-8")

    print("\n".join(changes) or "No changes.")
    if new_text == text:
        return 0
    if args.check:
        return 1
    args.readme.write_text(new_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
