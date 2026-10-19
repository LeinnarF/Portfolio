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
    "project": "PROJECT",
    "data": "DATA & ANALYTICS",
    "uiux": "UI/UX",
    "data-science": "DATA SCIENCE",
    "mobile": "MOBILE DEVELOPMENT",
    "web": "WEB DEVELOPMENT",
    "research": "RESEARCH",
}


class Link(BaseModel):
    label: str
    url: str


class Project(BaseModel):
    # identity
    slug: str
    type: str = "project"  # 'project' | 'data' | 'uiux' | any custom type

    # required content
    title: str
    summary: str  # short — used on the index row / card
    content: str = ""  # full rendered HTML body — set by the loader, not front matter

    # optional metadata
    description: Optional[str] = None  # longer description, if summary isn't enough
    tagline: Optional[str] = None  # overrides the category label on cards/detail page
    technologies: list[str] = Field(default_factory=list)
    disciplines: list[str] = Field(default_factory=list)
    discipline_labels: list[str] = Field(default_factory=list)
    year: Optional[int | str] = None
    date: Optional[str] = None
    order: int = 0
    featured: bool = False
    draft: bool = False

    # media
    cover_image: Optional[str] = None
    cover_width: Optional[int] = None
    cover_height: Optional[int] = None
    image_label: Optional[str] = None  # fallback text shown on the card if no cover_image

    # links
    links: list[Link] = Field(default_factory=list)

    @property
    def primary_discipline(self) -> str:
        if self.disciplines:
            return self.disciplines[0]
        return self.type

    @property
    def category_id(self) -> str:
        return self.primary_discipline

    @property
    def category_label(self) -> str:
        return CATEGORY_LABELS.get(self.category_id, self.category_id.replace("-", " ").upper())
