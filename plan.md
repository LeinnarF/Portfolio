# My Portfolio Project Plan

## Pipeline

```
                    ┌─────────────────────┐
                    │      CONTENT        │
                    │                     │
                    │  project.md         │
                    │  + front matter     │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │     LOAD / PARSE    │
                    │                     │
                    │  Markdown           │
                    │  YAML front matter  │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │    NORMALIZE DATA   │
                    │                     │
                    │  Project objects    │
                    │  metadata           │
                    │  HTML content       │
                    └──────────┬──────────┘
                ┌──────────────┴──────────────┐
                ▼                             ▼
       ┌─────────────────┐           ┌─────────────────┐
       │   JINJA INDEX   │           │  JINJA PROJECT  │
       │                 │           │                 │
       │ Data index      │           │ Project page    │
       │ UX index        │           │                 │
       │ Homepage        │           │                 │
       └────────┬────────┘           └────────┬────────┘
                └──────────────┬──────────────┘
                               ▼
                    ┌─────────────────────┐
                    │      BUILD          │
                    │                     │
                    │   /static/          │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │    STATIC WEBSITE   │
                    │                     │
                    │   index.html        │
                    │   data/...          │
                    │   uiux/...          │
                    └─────────────────────┘
```

## File Structure

```
.
├── content
│   ├── data
│   └── uiux
├── main.py
├── plan.md
├── script
├── static
│   └── index.html
└── templates
    ├── about.html
    ├── base.html
    ├── data.html
    ├── index.html
    ├── project.html
    └── uiux.html

```






