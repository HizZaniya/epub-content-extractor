import shutil
from pathlib import Path

from epub_content_extractor.extractor import extract_epub, get_epub_metadata, list_epub_spine


def test_extract_epub_creates_output_dir(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    extract_epub(reflowable_epub, output_dir)
    assert output_dir.is_dir()


def test_extract_epub_creates_chapter_files(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    extract_epub(reflowable_epub, output_dir)
    md_files = list(output_dir.glob("chapter_*.md"))
    assert len(md_files) == 2


def test_extract_epub_result_has_output_dir(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    result = extract_epub(reflowable_epub, output_dir)
    assert "output_dir" in result
    assert result["output_dir"] == str(output_dir)


def test_extract_epub_result_has_file_list(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    result = extract_epub(reflowable_epub, output_dir)
    assert "files" in result
    assert len(result["files"]) == 2


def test_extract_epub_default_output_dir(reflowable_epub: Path) -> None:
    result = extract_epub(reflowable_epub, None)
    expected_dir = reflowable_epub.parent / reflowable_epub.stem
    assert result["output_dir"] == str(expected_dir)
    shutil.rmtree(expected_dir, ignore_errors=True)


def test_extract_epub_with_images(epub_with_image: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    extract_epub(epub_with_image, output_dir)
    images_dir = output_dir / "images"
    assert images_dir.is_dir()
    assert len(list(images_dir.glob("*"))) == 1


def test_extract_epub_image_path_in_markdown(epub_with_image: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    extract_epub(epub_with_image, output_dir)
    md_files = sorted(output_dir.glob("chapter_*.md"))
    content = md_files[0].read_text(encoding="utf-8")
    assert "![](images/fig001.png)" in content


def test_get_epub_metadata(reflowable_epub: Path) -> None:
    result = get_epub_metadata(reflowable_epub)
    assert result["title"] == "Reflowable Test Book"
    assert result["language"] == "ja"
    assert result["layout"] == "reflowable"
    assert "Test Author" in result["authors"]


def test_list_epub_spine(reflowable_epub: Path) -> None:
    result = list_epub_spine(reflowable_epub)
    assert "spine" in result
    assert len(result["spine"]) == 2
    orders = [item["order"] for item in result["spine"]]
    assert orders == [1, 2]


def test_list_epub_spine_has_title(reflowable_epub: Path) -> None:
    result = list_epub_spine(reflowable_epub)
    titles = [item["title"] for item in result["spine"]]
    assert "Chapter 1" in titles
