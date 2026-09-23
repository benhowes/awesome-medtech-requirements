import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from sort_unmaintained import RepoStatus, rearrange, repos_in  # noqa: E402

NOW = datetime(2026, 9, 1, tzinfo=timezone.utc)
OLD = RepoStatus(archived=False, last_commit=datetime(2019, 5, 1, tzinfo=timezone.utc))
OLDER = RepoStatus(archived=False, last_commit=datetime(2016, 5, 1, tzinfo=timezone.utc))
FRESH = RepoStatus(archived=False, last_commit=datetime(2026, 8, 1, tzinfo=timezone.utc))
ARCHIVED = RepoStatus(archived=True, last_commit=datetime(2026, 1, 1, tzinfo=timezone.utc))

BEFORE = """# Title

## Contents
- [Tools](#tools)

## Tools

Intro text.

- **[Alive](https://github.com/a/alive)**
  Still going. 🆓
- **[Old](https://github.com/b/old)**
  Abandoned. 🆓
- **[Website](https://example.com/)**
  Not on GitHub. 💰
- **[Docs](https://docs.example.com/)** <!-- github: e/docs -->
  Docs site with a repo hint. 🆓
- **[Oldest](https://github.com/c/oldest/)**
  Very abandoned. 🆓

## Templates

- **[Archived](https://github.com/d/archived)** 🆓

Closing words.
"""

AFTER = """# Title

## Contents
- [Tools](#tools)

## Tools

Intro text.

- **[Alive](https://github.com/a/alive)**
  Still going. 🆓
- **[Website](https://example.com/)**
  Not on GitHub. 💰
- **[Docs](https://docs.example.com/)** <!-- github: e/docs -->
  Docs site with a repo hint. 🆓

<details>
<summary>Unmaintained (archived, or no commits in 2+ years)</summary>

- **[Old](https://github.com/b/old)** _(last commit 2019)_
  Abandoned. 🆓
- **[Oldest](https://github.com/c/oldest/)** _(last commit 2016)_
  Very abandoned. 🆓

</details>

## Templates

<details>
<summary>Unmaintained (archived, or no commits in 2+ years)</summary>

- **[Archived](https://github.com/d/archived)** 🆓 _(archived, last commit 2026)_

</details>

Closing words.
"""

STATUSES = {"a/alive": FRESH, "b/old": OLD, "c/oldest": OLDER, "d/archived": ARCHIVED, "e/docs": FRESH}


def test_repos_in_ignores_non_github_and_anchor_links():
    assert repos_in(BEFORE) == ["a/alive", "b/old", "e/docs", "c/oldest", "d/archived"]


def test_moves_stale_entries_into_details_newest_first():
    text, changes = rearrange(BEFORE, STATUSES, NOW, 2)
    assert text == AFTER
    assert len(changes) == 3


def test_is_idempotent():
    text, changes = rearrange(AFTER, STATUSES, NOW, 2)
    assert text == AFTER
    assert changes == []


def test_revived_entry_moves_back_and_loses_note():
    revived = {**STATUSES, "b/old": FRESH, "c/oldest": FRESH, "d/archived": FRESH}
    text, changes = rearrange(AFTER, revived, NOW, 2)
    assert "<details>" not in text
    assert "_(" not in text
    assert "- **[Oldest](https://github.com/c/oldest/)**\n  Very abandoned. 🆓\n\n## Templates" in text
    assert "- **[Archived](https://github.com/d/archived)** 🆓\n\nClosing words." in text
    assert len(changes) == 3


def test_unknown_status_leaves_entry_in_place():
    text, changes = rearrange(AFTER, {}, NOW, 2)
    assert text == AFTER
    assert changes == []


def test_readme_parses_without_changes_when_nothing_is_stale():
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
    statuses = {repo: FRESH for repo in repos_in(readme)}
    text, changes = rearrange(readme, statuses, NOW, 2)
    assert text == readme
    assert changes == []


def test_repo_hint_is_used_for_docs_sites():
    text, _ = rearrange(AFTER, {**STATUSES, "e/docs": OLD}, NOW, 2)
    assert "- **[Docs](https://docs.example.com/)** <!-- github: e/docs --> _(last commit 2019)_" in text
