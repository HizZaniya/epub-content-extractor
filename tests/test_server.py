import asyncio
from pathlib import Path

from epub_content_extractor.server import (
    _extract_epub_impl,
    _get_epub_metadata_impl,
    _list_epub_spine_impl,
    mcp,
)


def test_server_has_extract_epub_tool() -> None:
    tool_names = [t.name for t in asyncio.run(mcp.list_tools())]
    assert "extract_epub" in tool_names


def test_server_has_get_epub_metadata_tool() -> None:
    tool_names = [t.name for t in asyncio.run(mcp.list_tools())]
    assert "get_epub_metadata" in tool_names


def test_server_has_list_epub_spine_tool() -> None:
    tool_names = [t.name for t in asyncio.run(mcp.list_tools())]
    assert "list_epub_spine" in tool_names


def test_extract_epub_tool_result(reflowable_epub: Path, tmp_path: Path) -> None:
    result = _extract_epub_impl(str(reflowable_epub), str(tmp_path / "output"))
    assert "output_dir" in result
    assert "chapters" in result


def test_get_epub_metadata_tool_result(reflowable_epub: Path) -> None:
    result = _get_epub_metadata_impl(str(reflowable_epub))
    assert result["title"] == "Reflowable Test Book"
    assert result["language"] == "ja"


def test_list_epub_spine_tool_result(reflowable_epub: Path) -> None:
    result = _list_epub_spine_impl(str(reflowable_epub))
    assert "spine" in result
    assert len(result["spine"]) == 2
