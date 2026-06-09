from pathlib import Path

import ebooklib
from ebooklib import epub


def extract_images(book: epub.EpubBook, output_dir: Path) -> dict[str, Path]:
    """EPUB内の全画像を output_dir/images/ に保存し href→Path のマッピングを返す。"""
    mapping: dict[str, Path] = {}
    images_dir = output_dir / "images"

    for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
        images_dir.mkdir(parents=True, exist_ok=True)
        filename = Path(item.file_name).name
        dest = images_dir / filename
        dest.write_bytes(item.content)
        mapping[item.file_name] = dest

    return mapping
