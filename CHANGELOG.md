# Changelog

## v0.2.0 (2026-06-12)

### Feat

- add TestPyPI verification and approval gate before PyPI publish
- export public API from __init__.py
- implement FastMCP server with extract_epub, get_epub_metadata, list_epub_spine tools
- implement CLI entry point (typer)
- implement extractor (orchestration + AHL layout detection)
- implement markdown_writer (ContentBlock[] to Markdown with YAML front matter)
- implement image_extractor (EPUB images to output directory)
- implement content_converter (reflowable + fixed-layout HTML to ContentBlock)
- implement epub_reader (metadata + spine extraction)
- add shared data models (EpubMetadata, SpineItem, ContentBlock)

### Fix

- align TestPyPI propagation wait with PyPI (sleep 60)
- avoid double EPUB read in extractor and escape YAML string values
- remove unused tmp_path fixture in test_cli_nonexistent_file
- replace type: ignore with explicit Literal narrowing in epub_reader
- PRテンプレート検証失敗時に exit 2 を返すよう修正
