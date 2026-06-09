from epub_content_extractor.models import ContentBlock, EpubMetadata, SpineItem


def test_epub_metadata_reflowable() -> None:
    meta = EpubMetadata(
        title="Test Book",
        authors=["Author A"],
        language="ja",
        layout="reflowable",
        page_progression_direction="rtl",
        publisher=None,
        identifier=None,
    )
    assert meta.title == "Test Book"
    assert meta.layout == "reflowable"
    assert meta.page_progression_direction == "rtl"
    assert meta.publisher is None


def test_epub_metadata_fixed_layout() -> None:
    meta = EpubMetadata(
        title="Fixed",
        authors=[],
        language="ja",
        layout="fixed-layout",
        page_progression_direction="rtl",
        publisher="Publisher",
        identifier="urn:isbn:9784000000000",
    )
    assert meta.layout == "fixed-layout"
    assert meta.identifier == "urn:isbn:9784000000000"


def test_spine_item_creation() -> None:
    item = SpineItem(id="ch1", href="OEBPS/chapter01.xhtml", title="Chapter 1", order=1)
    assert item.id == "ch1"
    assert item.href == "OEBPS/chapter01.xhtml"
    assert item.order == 1


def test_spine_item_no_title() -> None:
    item = SpineItem(id="ch2", href="chapter02.xhtml", title=None, order=2)
    assert item.title is None


def test_content_block_heading() -> None:
    block = ContentBlock(type="heading", content="Chapter 1", level=1)
    assert block.type == "heading"
    assert block.level == 1


def test_content_block_paragraph() -> None:
    block = ContentBlock(type="paragraph", content="Hello World", level=None)
    assert block.type == "paragraph"
    assert block.level is None


def test_content_block_image() -> None:
    block = ContentBlock(type="image", content="images/fig001.png", level=None)
    assert block.type == "image"


def test_content_block_table() -> None:
    block = ContentBlock(type="table", content="| A | B |", level=None)
    assert block.type == "table"
