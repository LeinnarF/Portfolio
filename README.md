# Portfolio

A static portfolio site generator: write projects as Markdown files with
YAML front matter, get a static HTML site out. Built for a Data Science /
UI-UX portfolio, but the category system is generic — add a new
Markdown file directly to `content/` and it shows up on the homepage automatically.

## Quick start

```bash
pip install -r requirements.txt
python main.py serve
```

Open `http://localhost:8000`.

## How to use

### Development server (Live-reload)

Run the dev server with automatic rebuilding and browser live-reload:

```bash
python main.py serve
```

Any changes to Markdown files and site copy (`content/`), Jinja templates (`templates/`), or static assets (`assets/`) will automatically trigger an incremental in-process rebuild and refresh connected browser tabs. Changes to `src/` will automatically restart the server process.

**Options:**
- `--port`, `-p`: Port to serve on (default: `8000`)
  ```bash
  python main.py serve -p 8080
  ```
- `--host`: Host address to bind to (default: `127.0.0.1`)
  ```bash
  python main.py serve --host 0.0.0.0
  ```
- `--base-url`: Base URL prefix for testing subpath routing
  ```bash
  python main.py serve --base-url /Portfolio
  ```
- `--open`: Open the site in your default browser automatically on start
  ```bash
  python main.py serve --open
  ```
- `--no-watch`: Serve the `static/` folder statically without file watching or live-reload
  ```bash
  python main.py serve --no-watch
  ```

### Building static output

Generate the static HTML files directly into `static/` without running the server:

```bash
python main.py build
```

**Options:**
- `--base-url`: Prefix all internal and asset links with a base path (useful for GitHub Pages project sites like `https://username.github.io/repo-name`)
  ```bash
  python main.py build --base-url /Portfolio
  ```
- `--strict`: Fail with exit code 1 if any content front matter is invalid or malformed (recommended for CI pipelines)
  ```bash
  python main.py build --strict
  ```

The output in `static/` is ready to be deployed to any static hosting service (GitHub Pages, Cloudflare Pages, Netlify, Vercel, etc.). A GitHub Actions workflow is also provided at `.github/workflows/deploy.yml`.

## How it works

```
content/*.md        →  parser.py  →  loader.py  →  images.py  →  builder.py  →  static/
   (Markdown +           (front matter    (validates into  (WebP optimize,   (renders templates,
    front matter)         + body → HTML)   Project objects, unreferenced      outputs 404, sitemap)
                                           multidiscipline) assets pruned)
```

1. **`content/`** — one Markdown file per project directly in `content/` (single flat folder, no subsections needed), and `_site.yaml` for site-wide copy.
2. **`src/parser.py`** — splits a file into YAML front matter + Markdown
   body, parses inline `![[image]]` tags with dimensions and lazy loading, renders the body to HTML with code syntax highlighting tokens.
3. **`src/loader.py`** — walks `content/`, loads `content/_site.yaml`, validates each file's front
   matter into a `Project` (via `src/models.py`), skips anything invalid
   or marked `draft: true`, sorts, and groups by discipline.
4. **`src/images.py`** — optimizes referenced images to WebP, resizes large screenshots, caches output via mtime, syncs non-image assets incrementally, prunes unreferenced images, and auto-generates the Pygments code syntax highlighting CSS.
5. **`src/builder.py`** — renders `templates/index.html`, `templates/project.html`, `templates/404.html`, and `sitemap.xml` with Jinja2.
6. **`src/server.py`** — dev server with live-reload using `livereload`, watching source folders with incremental rebuilds and process restarting on `src/` changes.
7. **`main.py`** — CLI entry point (`build`, `serve`).

## Adding and Writing a Project

### 1. Create a Markdown file

Add a new Markdown file directly inside `content/` (such as `content/my-project.md`). The filename (without `.md`) becomes the project's URL slug:

- `content/my-project.md` → builds to `static/my-project/index.html` (accessible at `/my-project/`)

> [!TIP]
> If you use Obsidian, an authoring template with all metadata fields preconfigured is available at `_obsidian-templates/Project.md`.

### 2. Front matter structure

Every project file begins with YAML front matter enclosed between triple-dashed lines `---`:

```markdown
---
title: "Lakad Mobile Application"
summary: "A personalized mobile itinerary generator for cultural heritage and tourism in Bulacan."
disciplines:
  - mobile
  - uiux
  - research
year: 2025
technologies:
  - React Native
  - Figma
  - SQLite
tagline: "THESIS"
featured: true
order: 1
draft: false
links:
  - label: GitHub
    url: https://github.com/LeinnarF/lakad
  - label: Figma
    url: https://figma.com/file/example
---

## Overview

Write your project documentation here in standard Markdown. Headings (`##`, `###`),
paragraphs, bold/italic text, unordered/ordered lists, blockquotes, and tables are
fully styled.

### Code snippets
Fenced code blocks with language identifiers receive syntax highlighting:

```python
def calculate_metrics(data: list[float]) -> float:
    return sum(data) / len(data)
```

### Embedding images
Images placed in `assets/` can be embedded directly in the body using Obsidian-style syntax:

![[images/lakad.png|Interactive itinerary map view]]

The caption after `|` is optional. Images are automatically converted to optimized WebP
formats during build.
```

### 3. Metadata fields reference

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string | **Yes** | Project title displayed across cards, lists, detail pages, and `<title>`. |
| `summary` | string | **Yes** | Concise 1–2 sentence description shown on the homepage index list and project hero. |
| `disciplines` | list[string] | No | Disciplines covered (e.g. `[data-science, research]`). The **first** entry serves as the primary discipline. Every ID must exist in `content/_site.yaml` (validated in `--strict` mode). |
| `year` | int / string | No | Completion year (e.g. `2025` or `2024`). Displayed in the project index row and archive. |
| `technologies` | list[string] | No | Tools, libraries, and frameworks used (e.g. `[Python, PyTorch, Figma]`). Rendered as metadata tags. |
| `tagline` | string | No | Custom eyebrow label on the project page. Defaults to the primary discipline. |
| `featured` | boolean | No | Default `false`. If `true`, the project appears in the featured work list on the homepage. |
| `order` | int | No | Default `0`. Tiebreaker sorting priority within featured or unfeatured groups (lower numbers appear first). |
| `draft` | boolean | No | Default `false`. Set to `true` to keep work-in-progress drafts from appearing in the build output. |
| `links` | list[object] | No | Call-to-action buttons on the project page. Each item requires `label` and `url`. |

### 4. Adding or modifying disciplines

Disciplines are defined centrally in `content/_site.yaml` under `disciplines`:

```yaml
disciplines:
  - id: data-science
    label: "Data Science"
  - id: uiux
    label: "UI/UX"
  - id: mobile
    label: "Mobile Development"
  - id: web
    label: "Web Development"
  - id: research
    label: "Research"
```

To introduce a new discipline (e.g. `game-dev`), simply add it to `_site.yaml`. The site generator will automatically register the new filter and validate project front matter against it without requiring code modifications.

## Editing site-wide copy

Hero headline, about section, resume link, base URL, and footer links live in `content/_site.yaml` — edit them directly without touching Python code.

## Project structure

```
portfolio/
├── .github/workflows/  GitHub Actions CI/CD deployment
│   └── deploy.yml
├── content/            Source content — Markdown + front matter
│   ├── _site.yaml      Global site copy and configuration
│   ├── app-rating-prediction.md
│   └── ...             Projects live directly in content/ (no subfolders needed)
├── templates/          Jinja2 templates (base, index, project, 404)
├── assets/             Source assets (css, images, etc.)
│   ├── css/style.css
│   └── images/
├── static/             Generated output (WebP images, HTML, sitemap.xml)
├── src/                Build logic
│   ├── models.py       Pydantic Project/Link definitions
│   ├── parser.py       Front matter + Markdown → HTML, inline [[image]] syntax
│   ├── loader.py       Discovers content & loads _site.yaml into Projects
│   ├── images.py       WebP optimization, asset sync, syntax.css generation
│   ├── builder.py      Incremental site renderer, sitemap, 404
│   ├── server.py       Dev server with live-reload
│   └── utils.py        asset_url() and url_for() path helpers
├── main.py             CLI entry point
└── requirements.txt
```

## Requirements

- Python 3.10+
- `jinja2`, `markdown`, `pyyaml`, `pydantic`, `livereload`, `pillow`, `pygments` (see `requirements.txt`)
