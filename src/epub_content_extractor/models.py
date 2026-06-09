from dataclasses import dataclass
from typing import Literal


@dataclass
class EpubMetadata:
    title: str
    authors: list[str]
    language: str
    layout: Literal["reflowable", "fixed-layout", "ahl"]
    page_progression_direction: Literal["ltr", "rtl"]
    publisher: str | None
    identifier: str | None


@dataclass
class SpineItem:
    id: str
    href: str
    title: str | None
    order: int


@dataclass
class ContentBlock:
    type: Literal["heading", "paragraph", "image", "table"]
    content: str
    level: int | None = None
