# Changelog

## v0.2.6 (2026-06-14)

### Fix

- skip existing files on PyPI publish to prevent 400 error on re-release

## v0.2.5 (2026-06-13)

### Fix

- add --no-cache to uvx in verify-testpypi retry loop
- replace fixed sleep with retry loop in verify-testpypi job

## v0.2.4 (2026-06-13)

### Fix

- add skip_existing to TestPyPI publish step

## v0.2.3 (2026-06-13)

### Fix

- extract cover images by media_type instead of ITEM_IMAGE type

### Refactor

- extract _MINIMAL_PNG constant to remove duplication

## v0.2.2 (2026-06-13)

### Fix

- improve tag check robustness in release workflow
- handle missing tag in release workflow

## v0.2.1 (2026-06-12)

### Fix

- push tags explicitly to fix release workflow

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
