#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.31.0",
#     "click>=8.1.7",
# ]
# ///
"""Check the links in a markdown file.

External links are fetched; internal `#anchor` links are checked against the
file's headings. Sites that block bots (401/403/429) are reported as warnings
rather than failures unless --strict is given.

Usage:
    uv run scripts/check_links.py README.md
    uv run scripts/check_links.py README.md --base base.md   # only links not in base.md
"""

import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import click
import requests

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BARE_RE = re.compile(r"<(https?://[^>]+)>")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)
BOT_BLOCK_CODES = {401, 403, 429}

HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'),
    'Accept': ('text/html,application/xhtml+xml,application/xml;q=0.9,'
               'image/avif,image/webp,*/*;q=0.8'),
    'Accept-Language': 'en-US,en;q=0.5',
}

OK, WARN, FAIL = "✅", "⚠️", "❌"


def extract_links(content: str) -> list[tuple[str, str]]:
    """Return unique (text, url) pairs in document order."""
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    found = [(m.group(1), m.group(2)) for m in LINK_RE.finditer(content)]
    found += [(m.group(1), m.group(1)) for m in BARE_RE.finditer(content)]
    seen, links = set(), []
    for text, url in found:
        if url not in seen:
            seen.add(url)
            links.append((text, url))
    return links


def github_slug(heading: str) -> str:
    """Approximate GitHub's heading anchor algorithm."""
    heading = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return heading.replace(" ", "-")


def check_url(url: str, strict: bool) -> tuple[str, str]:
    base_url = url.split('#')[0]
    for attempt in range(2):
        try:
            response = requests.head(base_url, allow_redirects=True, timeout=15, headers=HEADERS)
            if response.status_code in (404, 405) or response.status_code >= 500:
                # Some servers mishandle HEAD; confirm with GET.
                response = requests.get(base_url, allow_redirects=True, timeout=15, headers=HEADERS)
            code = response.status_code
            if code < 400:
                return OK, f"OK ({code})"
            if code in BOT_BLOCK_CODES and not strict:
                return WARN, f"Blocked? ({code})"
            return FAIL, f"Error ({code})"
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
            if attempt == 0:
                continue
            kind = "Timeout" if isinstance(exc, requests.exceptions.Timeout) else "Connection error"
            return FAIL, kind
        except requests.exceptions.RequestException as exc:
            return FAIL, f"Error ({exc})"
    raise AssertionError("unreachable")


@click.command()
@click.argument('readme_path', type=click.Path(exists=True, path_type=Path), default='README.md')
@click.option('--base', type=click.Path(exists=True, path_type=Path),
              help='Only check links that are not already in this file (e.g. the base branch README).')
@click.option('--strict', is_flag=True, help='Treat 401/403/429 responses as failures.')
def main(readme_path: Path, base: Path | None, strict: bool):
    """Check all links in a markdown file and report their status."""
    content = readme_path.read_text(encoding='utf-8')
    links = extract_links(content)
    if base:
        known = {url for _, url in extract_links(base.read_text(encoding='utf-8'))}
        links = [(text, url) for text, url in links if url not in known]

    anchors = {github_slug(h) for h in HEADING_RE.findall(content)}
    results: list[tuple[str, str, str, str]] = []
    external = []
    for text, url in links:
        if url.startswith('#'):
            ok = url[1:] in anchors
            results.append((OK if ok else FAIL, text, url, "Anchor" if ok else "Missing anchor"))
        elif url.startswith(('http://', 'https://')):
            external.append((text, url))
        else:
            path_ok = (readme_path.parent / url.split('#')[0]).exists()
            results.append((OK if path_ok else FAIL, text, url, "File" if path_ok else "Missing file"))

    print(f"Checking {len(links)} links in {readme_path}...\n")
    with ThreadPoolExecutor(max_workers=8) as pool:
        statuses = pool.map(lambda link: check_url(link[1], strict), external)
        results += [(emoji, text, url, status) for (text, url), (emoji, status) in zip(external, statuses)]

    for emoji, text, url, status in results:
        print(f"{emoji} [{text}]({url}) - {status}")

    failures = [r for r in results if r[0] == FAIL]
    warnings = [r for r in results if r[0] == WARN]
    print(f"\n=== Summary ===\nChecked: {len(results)}  Failed: {len(failures)}  Warnings: {len(warnings)}")
    for label, group in (("Failed", failures), ("Warnings (possibly bot-blocked)", warnings)):
        if group:
            print(f"\n{label}:")
            for _, text, url, status in group:
                print(f"  • [{text}]({url}) - {status}")

    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
