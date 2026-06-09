from epub_content_extractor import __version__


def test_package_importable() -> None:
    assert __version__ is not None


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
