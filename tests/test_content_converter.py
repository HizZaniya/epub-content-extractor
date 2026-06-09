from epub_content_extractor.content_converter import convert_html


def test_heading_h1() -> None:
    html = b"<html><body><h1>Chapter 1</h1></body></html>"
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="ch.xhtml")
    assert len(blocks) == 1
    assert blocks[0].type == "heading"
    assert blocks[0].level == 1
    assert blocks[0].content == "Chapter 1"


def test_heading_levels() -> None:
    html = b"<html><body><h2>Section</h2><h3>Subsection</h3></body></html>"
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="ch.xhtml")
    assert blocks[0].level == 2
    assert blocks[1].level == 3


def test_paragraph() -> None:
    html = b"<html><body><p>Hello World</p></body></html>"
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="ch.xhtml")
    assert len(blocks) == 1
    assert blocks[0].type == "paragraph"
    assert blocks[0].content == "Hello World"


def test_empty_paragraph_skipped() -> None:
    html = b"<html><body><p></p><p>Text</p></body></html>"
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="ch.xhtml")
    assert len(blocks) == 1
    assert blocks[0].content == "Text"


def test_image_tag() -> None:
    html = b'<html><body><img src="../images/fig001.png" alt="fig"/></body></html>'
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="OEBPS/ch.xhtml")
    assert len(blocks) == 1
    assert blocks[0].type == "image"
    assert "fig001.png" in blocks[0].content


def test_image_src_resolved() -> None:
    html = b'<html><body><img src="../images/fig001.png"/></body></html>'
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="OEBPS/Text/ch.xhtml")
    # resolved: OEBPS/images/fig001.png
    assert blocks[0].content == "OEBPS/images/fig001.png"


def test_table() -> None:
    html = b"<html><body><table><tr><td>A</td><td>B</td></tr></table></body></html>"
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="ch.xhtml")
    assert len(blocks) == 1
    assert blocks[0].type == "table"
    assert "A" in blocks[0].content
    assert "B" in blocks[0].content


def test_multiple_blocks_in_order() -> None:
    html = b"<html><body><h1>Title</h1><p>Para</p></body></html>"
    blocks = convert_html(html, layout="reflowable", ppd="ltr", spine_href="ch.xhtml")
    assert blocks[0].type == "heading"
    assert blocks[1].type == "paragraph"


def test_fixed_layout_rtl_order() -> None:
    html = (
        b"<html><body>"
        b'<div style="position: absolute; left: 700px; top: 100px;">Right</div>'
        b'<div style="position: absolute; left: 100px; top: 100px;">Left</div>'
        b"</body></html>"
    )
    blocks = convert_html(html, layout="fixed-layout", ppd="rtl", spine_href="page.xhtml")
    assert blocks[0].content == "Right"
    assert blocks[1].content == "Left"


def test_fixed_layout_ltr_order() -> None:
    html = (
        b"<html><body>"
        b'<div style="position: absolute; left: 700px; top: 100px;">Right</div>'
        b'<div style="position: absolute; left: 100px; top: 100px;">Left</div>'
        b"</body></html>"
    )
    blocks = convert_html(html, layout="fixed-layout", ppd="ltr", spine_href="page.xhtml")
    assert blocks[0].content == "Left"
    assert blocks[1].content == "Right"


def test_fixed_layout_column_y_order() -> None:
    html = (
        b"<html><body>"
        b'<div style="position: absolute; left: 700px; top: 200px;">Second</div>'
        b'<div style="position: absolute; left: 700px; top: 100px;">First</div>'
        b"</body></html>"
    )
    blocks = convert_html(html, layout="fixed-layout", ppd="rtl", spine_href="page.xhtml")
    assert blocks[0].content == "First"
    assert blocks[1].content == "Second"
