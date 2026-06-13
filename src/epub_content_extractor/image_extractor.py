from pathlib import Path

from ebooklib import epub


def extract_images(book: epub.EpubBook, output_dir: Path) -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    images_dir = output_dir / "images"

    for item in book.get_items():
        if not (item.media_type and item.media_type.startswith("image/")):
            continue
        images_dir.mkdir(parents=True, exist_ok=True)
        filename = Path(item.file_name).name
        dest = images_dir / filename
        dest.write_bytes(item.content)
        mapping[item.file_name] = dest

    return mapping
