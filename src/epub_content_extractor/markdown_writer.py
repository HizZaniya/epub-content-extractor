from pathlib import Path

from epub_content_extractor.models import ContentBlock, EpubMetadata, SpineItem


def write_chapter(
    blocks: list[ContentBlock],
    metadata: EpubMetadata,
    spine_item: SpineItem,
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"chapter_{spine_item.order:03d}.md"
    path = output_dir / filename

    lines: list[str] = []
    lines.append(_front_matter(metadata, spine_item))
    lines.append("")

    for block in blocks:
        lines.append(_render_block(block))
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _yaml_str(value: str) -> str:
    return value.replace('"', '\\"')


def _front_matter(metadata: EpubMetadata, spine_item: SpineItem) -> str:
    authors_yaml = "\n".join(f'  - "{_yaml_str(a)}"' for a in metadata.authors)
    publisher = (
        f'publisher: "{_yaml_str(metadata.publisher)}"' if metadata.publisher else "publisher: null"
    )
    identifier = (
        f'identifier: "{_yaml_str(metadata.identifier)}"'
        if metadata.identifier
        else "identifier: null"
    )
    chapter_title = (
        f'chapter_title: "{_yaml_str(spine_item.title)}"'
        if spine_item.title
        else "chapter_title: null"
    )
    return "\n".join(
        [
            "---",
            f'title: "{_yaml_str(metadata.title)}"',
            "authors:",
            authors_yaml,
            f"language: {metadata.language}",
            publisher,
            identifier,
            f"epub_layout: {metadata.layout}",
            f"page_progression_direction: {metadata.page_progression_direction}",
            chapter_title,
            f"spine_order: {spine_item.order}",
            "---",
        ]
    )


def _render_block(block: ContentBlock) -> str:
    if block.type == "heading":
        level = block.level or 1
        return "#" * level + " " + block.content
    if block.type == "paragraph":
        return block.content
    if block.type == "image":
        return f"![]({block.content})"
    if block.type == "table":
        return block.content
    return block.content
