from __future__ import annotations

import argparse
import re
import shutil
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html import unescape
from pathlib import Path


NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
    "wp": "http://wordpress.org/export/1.2/",
}


SECTION_MAP = {
    "movies-and-series": "reviews",
    "travel": "itineraries",
    "thought": "thoughts",
    "uncategorized": "thoughts",
}


@dataclass
class PostRecord:
    title: str
    slug: str
    date: str
    content: str
    excerpt: str
    post_type: str
    status: str
    categories: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


def text_or_empty(node: ET.Element | None, path: str) -> str:
    if node is None:
        return ""
    child = node.find(path, NS)
    if child is None or child.text is None:
        return ""
    return child.text.strip()


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()


def strip_html(value: str) -> str:
    return normalize_text(re.sub(r"<[^>]+>", " ", value))


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "post"


def toml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    escaped = escaped.replace("\n", " ").replace("\r", " ")
    return f'"{escaped}"'


def parse_items(xml_path: Path) -> list[PostRecord]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    channel = root.find("channel")
    if channel is None:
        raise ValueError("Invalid WordPress export: missing channel element.")

    records: list[PostRecord] = []
    for item in channel.findall("item"):
        title = text_or_empty(item, "title")
        post_type = text_or_empty(item, "wp:post_type")
        status = text_or_empty(item, "wp:status")
        if status != "publish" or post_type not in {"post", "page"}:
            continue

        slug = text_or_empty(item, "wp:post_name") or slugify(title)
        date = text_or_empty(item, "wp:post_date")
        content = text_or_empty(item, "content:encoded")
        excerpt = text_or_empty(item, "excerpt:encoded")
        categories: list[str] = []
        tags: list[str] = []

        for category in item.findall("category"):
            domain = category.attrib.get("domain", "")
            name = normalize_text(category.text or "")
            nicename = category.attrib.get("nicename", "")
            if not name and not nicename:
                continue
            value = nicename or slugify(name)
            if domain == "category":
                categories.append(value)
            elif domain == "post_tag":
                tags.append(value)

        records.append(
            PostRecord(
                title=normalize_text(title) or slug,
                slug=slugify(slug),
                date=date,
                content=content.strip(),
                excerpt=strip_html(excerpt),
                post_type=post_type,
                status=status,
                categories=sorted(set(categories)),
                tags=sorted(set(tags)),
            )
        )
    return records


def resolve_section(record: PostRecord) -> str:
    if record.post_type == "page":
        return "pages"
    for category in record.categories:
        if category in SECTION_MAP:
            return SECTION_MAP[category]
    return "thoughts"


def build_front_matter(record: PostRecord, section: str) -> str:
    summary = record.excerpt
    if not summary:
        summary = strip_html(record.content)[:180].rstrip()

    year = record.date[:4] if record.date else ""
    front_matter = [
        "+++",
        f"title = {toml_string(record.title)}",
        f"date = {record.date.replace(' ', 'T')}+00:00" if record.date else "",
        "draft = false",
        f"type = {toml_string(section)}",
        f"slug = {toml_string(record.slug)}",
    ]

    if summary:
        front_matter.append(f"summary = {toml_string(summary)}")
    if record.categories:
        front_matter.append("categories = [" + ", ".join(toml_string(c) for c in record.categories) + "]")
    if record.tags:
        front_matter.append("tags = [" + ", ".join(toml_string(t) for t in record.tags) + "]")
    if section == "reviews" and year:
        front_matter.append(f"year = {toml_string(year)}")
        front_matter.append(f"years = [{toml_string(year)}]")
    if section == "itineraries":
        destination = destination_from_title(record.title)
        if destination:
            front_matter.append(f"destinations = [{toml_string(destination)}]")

    front_matter.append("+++")
    return "\n".join(line for line in front_matter if line)


def destination_from_title(title: str) -> str:
    cleaned = re.sub(r"\b(itinerary|trip|cancelled)\b", "", title, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b\d{4}\b", "", cleaned)
    cleaned = normalize_text(cleaned)
    return slugify(cleaned) if cleaned else ""


def write_content(records: list[PostRecord], output_dir: Path) -> None:
    generated_dir = output_dir / "content"
    for record in records:
        section = resolve_section(record)
        target = generated_dir / section / f"{record.slug}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        body = record.content or textwrap.dedent(
            """
            <p>This post was imported from WordPress, but the original body was empty.</p>
            """
        ).strip()
        target.write_text(build_front_matter(record, section) + "\n\n" + body + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a WordPress XML export into this Hugo site.")
    parser.add_argument("xml_path", type=Path, help="Path to the WordPress XML export.")
    parser.add_argument(
        "--site-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the Hugo site root. Defaults to the repository root.",
    )
    parser.add_argument(
        "--copy-source",
        action="store_true",
        help="Copy the WordPress XML into data/wordpress/original.xml for reference.",
    )
    args = parser.parse_args()

    xml_path = args.xml_path.resolve()
    site_root = args.site_root.resolve()
    if not xml_path.exists():
        raise SystemExit(f"WordPress export not found: {xml_path}")

    records = parse_items(xml_path)
    write_content(records, site_root)

    if args.copy_source:
        source_target = site_root / "data" / "wordpress" / "original.xml"
        source_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(xml_path, source_target)

    print(f"Imported {len(records)} published posts/pages into {site_root / 'content'}")


if __name__ == "__main__":
    main()

