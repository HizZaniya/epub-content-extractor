from pathlib import Path

from ebooklib import epub

from epub_content_extractor.image_extractor import extract_images


def test_extract_images_creates_directory(epub_with_image: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    book = epub.read_epub(str(epub_with_image), {"ignore_ncx": True})
    extract_images(book, output_dir)
    assert (output_dir / "images").is_dir()


def test_extract_images_saves_file(epub_with_image: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    book = epub.read_epub(str(epub_with_image), {"ignore_ncx": True})
    mapping = extract_images(book, output_dir)
    assert len(mapping) == 1
    saved_path = next(iter(mapping.values()))
    assert saved_path.exists()


def test_extract_images_returns_mapping(epub_with_image: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    book = epub.read_epub(str(epub_with_image), {"ignore_ncx": True})
    mapping = extract_images(book, output_dir)
    epub_hrefs = list(mapping.keys())
    assert any("fig001.png" in h for h in epub_hrefs)


def test_extract_images_filename(epub_with_image: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    book = epub.read_epub(str(epub_with_image), {"ignore_ncx": True})
    mapping = extract_images(book, output_dir)
    saved = next(iter(mapping.values()))
    assert saved.name == "fig001.png"
    assert saved.parent.name == "images"


def test_no_images_returns_empty(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    book = epub.read_epub(str(reflowable_epub), {"ignore_ncx": True})
    mapping = extract_images(book, output_dir)
    assert mapping == {}
