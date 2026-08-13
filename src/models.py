"""
Data models for the portfolio site.

Using Pydantic instead of a plain dataclass so malformed front matter
(missing required field, wrong type in `technologies`, etc.) fails loudly
and specifically at build time instead of surfacing as a vague Jinja
AttributeError mid-render.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


CATEGORY_LABELS = {
    "data": "DATA & ANALYTICS",
    "uiux": "UI/UX",
}


class Link(BaseModel):
    label: str
    url: str


class GalleryImage(BaseModel):
    path: str
    caption: Optional[str] = None


class Project(BaseModel):
    # identity
    slug: str
    type: str  # 'data' | 'uiux' | any future category — matches content/<type>/ folder

    # required content
    title: str
    summary: str  # short — used on the index card
    content: str = ""  # full rendered HTML body — set by the loader, not front matter

    # optional metadata
    description: Optional[str] = None  # longer description, if summary isn't enough
    tagline: Optional[str] = None  # overrides the category label on cards/detail page
    technologies: list[str] = Field(default_factory=list)
    date: Optional[str] = None
    order: int = 0
    featured: bool = False
    draft: bool = False

    # media
    cover_image: Optional[str] = None
    image_label: Optional[str] = None  # fallback text shown on the card if no cover_image
    gallery: list[GalleryImage] = Field(default_factory=list)

    # links
    links: list[Link] = Field(default_factory=list)

    @property
    def category_id(self) -> str:
        return self.type

    @property
    def category_label(self) -> str:
        return CATEGORY_LABELS.get(self.type, self.type.upper())
