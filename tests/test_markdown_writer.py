from pathlib import Path

import pytest

from epub_content_extractor.markdown_writer import write_chapter
from epub_content_extractor.models import ContentBlock, EpubMetadata, SpineItem


@pytest.fixture
def sample_metadata() -> EpubMetadata:
    return EpubMetadata(
        title="Test Book",
        authors=["Author A"],
        language="ja",
        layout="reflowable",
        page_progression_direction="rtl",
        publisher="Test Publisher",
        identifier="urn:isbn:9784000000000",
    )


@pytest.fixture
def sample_spine_item() -> SpineItem:
    return SpineItem(id="ch1", href="chapter01.xhtml", title="Chapter 1", order=1)


def test_write_chapter_creates_file(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks = [ContentBlock(type="paragraph", content="Hello World")]
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    assert (tmp_path / "chapter_001.md").exists()


def test_write_chapter_filename_uses_order(tmp_path: Path, sample_metadata: EpubMetadata) -> None:
    item = SpineItem(id="ch5", href="ch5.xhtml", title="Chapter 5", order=5)
    blocks: list[ContentBlock] = []
    write_chapter(blocks, sample_metadata, item, tmp_path)
    assert (tmp_path / "chapter_005.md").exists()


def test_yaml_front_matter(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks: list[ContentBlock] = []
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert 'title: "Test Book"' in content
    assert "language: ja" in content
    assert 'chapter_title: "Chapter 1"' in content
    assert "spine_order: 1" in content
    assert "epub_layout: reflowable" in content
    assert "page_progression_direction: rtl" in content


def test_heading_output(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks = [ContentBlock(type="heading", content="My Heading", level=1)]
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert "# My Heading" in content


def test_heading_level_2(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks = [ContentBlock(type="heading", content="Section", level=2)]
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert "## Section" in content


def test_paragraph_output(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks = [ContentBlock(type="paragraph", content="Hello World")]
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert "Hello World" in content


def test_image_output(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks = [ContentBlock(type="image", content="images/fig001.png")]
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert "![](images/fig001.png)" in content


def test_table_output(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks = [ContentBlock(type="table", content="| A | B |")]
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert "| A | B |" in content


def test_authors_in_front_matter(
    tmp_path: Path, sample_metadata: EpubMetadata, sample_spine_item: SpineItem
) -> None:
    blocks: list[ContentBlock] = []
    write_chapter(blocks, sample_metadata, sample_spine_item, tmp_path)
    content = (tmp_path / "chapter_001.md").read_text(encoding="utf-8")
    assert "- Author A" in content
