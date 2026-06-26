#!/usr/bin/env python
"""Validate the static Sweet Beans website before publishing.

No external dependencies. Checks required files, local links/assets, basic
HTML shape, and obvious secret leakage patterns.
"""
from __future__ import annotations

import argparse
import html.parser
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urlparse, unquote

ATTRS_TO_CHECK = {"href", "src", "poster"}
REQUIRED_FILES = ["index.html", "styles.css", ".nojekyll"]
SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}"),
]
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "data", "sms"}
TEXT_EXTENSIONS = {".html", ".css", ".js", ".json", ".xml", ".txt", ".svg", ".md"}


class LinkParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[int, str, str]] = []
        self.ids: set[str] = set()
        self.has_description = False
        self.has_viewport = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): v for k, v in attrs if v is not None}
        if "id" in attrs_dict:
            self.ids.add(attrs_dict["id"])
        for attr in ATTRS_TO_CHECK:
            if attr in attrs_dict:
                self.links.append((self.getpos()[0], attr, attrs_dict[attr]))
        if tag.lower() == "meta":
            name = attrs_dict.get("name", "").lower()
            if name == "description" and attrs_dict.get("content", "").strip():
                self.has_description = True
            if name == "viewport":
                self.has_viewport = True

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def iter_published_files(root: Path) -> list[Path]:
    ignored_parts = {".git", ".github", "scripts", "archive"}
    ignored_names = {
        "CNAME",  # kept for later DNS, excluded from current Pages artifact.
    }
    files: list[Path] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in ignored_parts for part in rel.parts):
            continue
        if path.name in ignored_names:
            continue
        files.append(path)
    return files


def check_required(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")


def check_secrets(root: Path, errors: list[str]) -> None:
    for path in iter_published_files(root):
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                rel = path.relative_to(root)
                errors.append(f"possible secret in {rel}: matched {pattern.pattern!r}")
                break


def resolve_local_target(root: Path, html_file: Path, raw_url: str) -> tuple[Path | None, str]:
    url_no_fragment, fragment = urldefrag(raw_url.strip())
    parsed = urlparse(url_no_fragment)
    if parsed.scheme.lower() in SKIP_SCHEMES or parsed.netloc:
        return None, fragment
    path_only = parsed.path
    if not path_only:
        return html_file, fragment
    decoded = unquote(path_only)
    if decoded.startswith("/"):
        target = root / decoded.lstrip("/")
    else:
        target = html_file.parent / decoded
    return target.resolve(), fragment


def check_html(root: Path, errors: list[str]) -> None:
    html_files = sorted(root.glob("*.html"))
    if not html_files:
        errors.append("no top-level HTML files found")
        return

    root_resolved = root.resolve()
    for html_file in html_files:
        rel_html = html_file.relative_to(root)
        text = html_file.read_text(encoding="utf-8", errors="ignore")
        parser = LinkParser()
        parser.feed(text)

        if not re.search(r"<title>\s*\S", text, re.I):
            errors.append(f"{rel_html}: missing non-empty <title>")
        if not parser.has_description:
            errors.append(f"{rel_html}: missing meta description")
        if not parser.has_viewport:
            errors.append(f"{rel_html}: missing viewport meta tag")

        for line, attr, raw_url in parser.links:
            target, fragment = resolve_local_target(root, html_file, raw_url)
            if target is None:
                continue
            try:
                target.relative_to(root_resolved)
            except ValueError:
                errors.append(f"{rel_html}:{line}: {attr} escapes site root: {raw_url}")
                continue
            if not target.exists():
                errors.append(f"{rel_html}:{line}: missing local {attr}: {raw_url}")
                continue
            if fragment and target.suffix.lower() == ".html":
                target_text = target.read_text(encoding="utf-8", errors="ignore")
                target_parser = LinkParser()
                target_parser.feed(target_text)
                if fragment not in target_parser.ids:
                    errors.append(f"{rel_html}:{line}: missing fragment #{fragment} in {target.relative_to(root)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site", nargs="?", default=".", help="static site directory")
    args = parser.parse_args()

    root = Path(args.site).resolve()
    errors: list[str] = []
    if not root.is_dir():
        print(f"ERROR: site directory not found: {root}", file=sys.stderr)
        return 1

    check_required(root, errors)
    check_html(root, errors)
    check_secrets(root, errors)

    if errors:
        print("Static site validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    files = iter_published_files(root)
    print(f"Static site validation passed: {len(files)} publishable files checked under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
