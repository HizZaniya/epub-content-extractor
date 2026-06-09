from pathlib import Path

import pytest

from epub_content_extractor.epub_reader import read_epub
from epub_content_extractor.models import EpubMetadata, SpineItem


def test_read_metadata_reflowable(reflowable_epub: Path) -> None:
    metadata, _ = read_epub(reflowable_epub)
    assert isinstance(metadata, EpubMetadata)
    assert metadata.title == "Reflowable Test Book"
    assert metadata.authors == ["Test Author"]
    assert metadata.language == "ja"
    assert metadata.layout == "reflowable"
    assert metadata.page_progression_direction == "rtl"


def test_read_metadata_fixed(fixed_epub: Path) -> None:
    metadata, _ = read_epub(fixed_epub)
    assert metadata.layout == "fixed-layout"
    assert metadata.page_progression_direction == "rtl"


def test_read_spine_items(reflowable_epub: Path) -> None:
    _, spine_items = read_epub(reflowable_epub)
    assert len(spine_items) == 2
    assert all(isinstance(item, SpineItem) for item in spine_items)


def test_spine_items_ordered(reflowable_epub: Path) -> None:
    _, spine_items = read_epub(reflowable_epub)
    orders = [item.order for item in spine_items]
    assert orders == sorted(orders)
    assert orders[0] == 1


def test_spine_items_have_title(reflowable_epub: Path) -> None:
    _, spine_items = read_epub(reflowable_epub)
    titles = [item.title for item in spine_items]
    assert "Chapter 1" in titles


def test_spine_items_have_href(reflowable_epub: Path) -> None:
    _, spine_items = read_epub(reflowable_epub)
    hrefs = [item.href for item in spine_items]
    assert any("chapter01.xhtml" in h for h in hrefs)


def test_epub_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        read_epub(Path("/nonexistent/path.epub"))
