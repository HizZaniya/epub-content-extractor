from pathlib import Path

from typer.testing import CliRunner

from epub_content_extractor.cli import app

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "INPUT" in result.output


def test_cli_extract_creates_output(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = str(tmp_path / "output")
    result = runner.invoke(app, [str(reflowable_epub), output_dir])
    assert result.exit_code == 0
    assert (tmp_path / "output").is_dir()


def test_cli_extract_success_message(reflowable_epub: Path, tmp_path: Path) -> None:
    output_dir = str(tmp_path / "output")
    result = runner.invoke(app, [str(reflowable_epub), output_dir])
    assert result.exit_code == 0
    assert "chapter" in result.output.lower() or "extracted" in result.output.lower()


def test_cli_nonexistent_file() -> None:
    result = runner.invoke(app, ["/nonexistent/path.epub"])
    assert result.exit_code != 0


def test_cli_default_output_dir(reflowable_epub: Path) -> None:
    result = runner.invoke(app, [str(reflowable_epub)])
    assert result.exit_code == 0
    expected_dir = reflowable_epub.parent / reflowable_epub.stem
    assert expected_dir.is_dir()
    import shutil

    shutil.rmtree(expected_dir, ignore_errors=True)
