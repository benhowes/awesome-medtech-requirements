import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from check_links import extract_links, github_slug  # noqa: E402


def test_extract_links_dedupes_and_ignores_comments():
    content = "[a](https://a.com) [b](https://a.com) <!-- [c](https://c.com) --> <https://d.com>"
    assert extract_links(content) == [("a", "https://a.com"), ("https://d.com", "https://d.com")]


def test_github_slug():
    assert github_slug("Academic Projects & Research") == "academic-projects--research"
    assert github_slug("Requirements Management Tools (in Jira)") == "requirements-management-tools-in-jira"
