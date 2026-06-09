import pytest
from ebooklib import epub


@pytest.fixture
def reflowable_epub(tmp_path):
    """最小限のリフロー型EPUBを生成する。"""
    book = epub.EpubBook()
    book.set_identifier("test-reflowable-1")
    book.set_title("Reflowable Test Book")
    book.set_language("ja")
    book.add_author("Test Author")
    book.add_metadata(None, "meta", "reflowable", {"property": "rendition:layout"})
    book.add_metadata(None, "meta", "rtl", {"property": "page-progression-direction"})

    ch1 = epub.EpubHtml(title="Chapter 1", file_name="chapter01.xhtml", lang="ja")
    ch1.content = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b"<html><body>"
        b"<h1>Chapter 1</h1>"
        b"<p>Hello World</p>"
        b"<h2>Section 1.1</h2>"
        b"<p>Paragraph text.</p>"
        b"</body></html>"
    )

    ch2 = epub.EpubHtml(title="Chapter 2", file_name="chapter02.xhtml", lang="ja")
    ch2.content = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b"<html><body>"
        b"<h1>Chapter 2</h1>"
        b"<p>Second chapter.</p>"
        b"</body></html>"
    )

    nav = epub.EpubNav()
    book.add_item(ch1)
    book.add_item(ch2)
    book.add_item(nav)
    book.toc = [ch1, ch2]
    book.spine = ["nav", ch1, ch2]

    path = tmp_path / "reflowable.epub"
    epub.write_epub(str(path), book)
    return path


@pytest.fixture
def fixed_epub(tmp_path):
    """最小限のフィックス型EPUB(rtl)を生成する。"""
    book = epub.EpubBook()
    book.set_identifier("test-fixed-1")
    book.set_title("Fixed Layout Test Book")
    book.set_language("ja")
    book.add_author("Test Author")
    book.add_metadata(None, "meta", "pre-paginated", {"property": "rendition:layout"})
    book.add_metadata(None, "meta", "rtl", {"property": "page-progression-direction"})

    page1 = epub.EpubHtml(title="Page 1", file_name="page01.xhtml", lang="ja")
    page1.content = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b"<html><body>"
        b'<div style="position: absolute; left: 700px; top: 100px;">Right text</div>'
        b'<div style="position: absolute; left: 100px; top: 100px;">Left text</div>'
        b'<div style="position: absolute; left: 700px; top: 200px;">Right second</div>'
        b"</body></html>"
    )

    nav = epub.EpubNav()
    book.add_item(page1)
    book.add_item(nav)
    book.toc = []
    book.spine = ["nav", page1]

    path = tmp_path / "fixed.epub"
    epub.write_epub(str(path), book)
    return path


@pytest.fixture
def epub_with_image(tmp_path):
    """画像を含むリフロー型EPUBを生成する。"""
    book = epub.EpubBook()
    book.set_identifier("test-image-1")
    book.set_title("Image Test Book")
    book.set_language("ja")
    book.add_author("Test Author")

    # 1x1の白ピクセルPNG(最小PNG)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
        b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
        b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    img = epub.EpubImage()
    img.id = "img1"
    img.file_name = "images/fig001.png"
    img.media_type = "image/png"
    img.content = png_bytes

    ch1 = epub.EpubHtml(title="Chapter 1", file_name="chapter01.xhtml", lang="ja")
    ch1.content = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b"<html><body>"
        b"<h1>Chapter 1</h1>"
        b'<img src="../images/fig001.png" alt="Figure 1"/>'
        b"<p>Caption text.</p>"
        b"</body></html>"
    )

    nav = epub.EpubNav()
    book.add_item(img)
    book.add_item(ch1)
    book.add_item(nav)
    book.toc = [ch1]
    book.spine = ["nav", ch1]

    path = tmp_path / "with_image.epub"
    epub.write_epub(str(path), book)
    return path
