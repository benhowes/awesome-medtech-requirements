#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests>=2.31.0",
#     "click>=8.1.7",
#     "markdown>=3.5.2",
# ]
# ///

import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Tuple, Dict, List

import click
import requests
from markdown import Markdown
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension


class LinkExtractor(Preprocessor):
    def __init__(self, md):
        super().__init__(md)
        self.links = []

    def run(self, lines):
        for line in lines:
            # Match markdown links [text](url)
            matches = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line)
            for match in matches:
                self.links.append((match.group(1), match.group(2)))

            # Match bare URLs in angle brackets
            matches = re.finditer(r'<(https?://[^>]+)>', line)
            for match in matches:
                self.links.append((match.group(1), match.group(1)))
        return lines


class LinkExtractorExtension(Extension):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.links = []

    def extendMarkdown(self, md):
        link_extractor = LinkExtractor(md)
        md.preprocessors.register(link_extractor, 'link_extractor', 25)
        self.links = link_extractor.links


HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'),
    'Accept': ('text/html,application/xhtml+xml,application/xml;q=0.9,'
              'image/avif,image/webp,*/*;q=0.8'),
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}


def check_url(url: str) -> Tuple[bool, str, str]:
    """Check if a URL is accessible and return status."""
    try:
        # Handle fragments by removing them before checking
        base_url = url.split('#')[0]

        # Skip non-http(s) URLs
        if not base_url.startswith(('http://', 'https://')):
            return True, "✅", "Skipped (not HTTP/HTTPS)"

        response = requests.head(base_url, allow_redirects=True,
                               timeout=10, headers=HEADERS)
        if response.status_code == 405:  # If HEAD not allowed, try GET
            response = requests.get(base_url, allow_redirects=True,
                                  timeout=10, headers=HEADERS)

        if response.status_code < 400:
            return True, "✅", f"OK ({response.status_code})"
        else:
            return False, "❌", f"Error ({response.status_code})"

    except requests.exceptions.Timeout:
        return False, "⌛", "Timeout"
    except requests.exceptions.SSLError:
        return False, "🔒", "SSL Error"
    except requests.exceptions.ConnectionError:
        return False, "🔌", "Connection Error"
    except Exception as e:
        return False, "❓", f"Unknown Error ({str(e)})"


def print_summary(results: Dict[str, List[Tuple[str, str]]]) -> None:
    """Print a summary of link check results."""
    total = sum(len(links) for links in results.values())
    errors = sum(len(links) for status, links in results.items() if status != "OK")

    print("\n=== Summary ===")
    print(f"Total links checked: {total}")
    print(f"Success: {total - errors}")
    print(f"Errors: {errors}")

    if errors > 0:
        print("\n=== Failed Links ===")
        for status, links in results.items():
            if status != "OK" and links:
                print(f"\n{status}:")
                for text, url in links:
                    print(f"  • [{text}]({url})")


@click.command()
@click.argument('readme_path', type=click.Path(exists=True), default='README.md')
def main(readme_path: str):
    """Check all links in a markdown file and report their status."""
    readme = Path(readme_path)
    content = readme.read_text(encoding='utf-8')

    # Extract links
    ext = LinkExtractorExtension()
    md = Markdown(extensions=[ext])
    md.convert(content)
    links = ext.links

    if not links:
        print("No links found in the document!")
        return

    print(f"\nChecking {len(links)} links in {readme_path}...\n")

    # Track results by status
    results = defaultdict(list)
    has_errors = False

    for text, url in links:
        success, emoji, status = check_url(url)
        if not success:
            has_errors = True
            status_key = status.split(" (")[0]  # Extract main status
            results[status_key].append((text, url))
        else:
            results["OK"].append((text, url))
        print(f"{emoji} [{text}]({url}) - {status}")

    print_summary(results)

    if has_errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
