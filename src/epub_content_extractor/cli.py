from pathlib import Path

import typer

from epub_content_extractor.extractor import extract_epub

app = typer.Typer(help="Extract text and images from EPUB files as Markdown.")


@app.command()
def main(
    input: Path = typer.Argument(..., help="Path to the EPUB file."),
    output_dir: Path | None = typer.Argument(
        None, help="Output directory (default: {epub_dir}/{epub_stem}/)."
    ),
) -> None:
    if not input.exists():
        typer.echo(f"Error: File not found: {input}", err=True)
        raise typer.Exit(code=1)

    result = extract_epub(input, output_dir)
    typer.echo(f"Extracted {result['chapters']} chapter(s) to {result['output_dir']}")
    for f in result["files"]:
        typer.echo(f"  {f}")
