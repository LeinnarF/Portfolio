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
portfolio/
│
├── content/              ← SOURCE CONTENT
│   ├── data/
│   └── uiux/
│
├── templates/            ← PRESENTATION
│   ├── base.html
│   ├── index.html
│   ├── data.html
│   ├── uiux.html
│   └── project.html
│
├── assets/               ← SOURCE ASSETS
│   ├── images/
│   ├── css/
│   └── js/
│
├── static/               ← GENERATED OUTPUT
│
├── src/                  ← BUILD LOGIC
│   ├── loader.py
│   ├── parser.py
│   ├── builder.py
│   └── models.py
│
├── main.py
└── requirements.txt
```

## Phases

### **Phase 1: Content Creation**
- From `content/` and `content/`, create Markdown files for each project.
- YAML front matter for each project.
- Markdown content for each project.


### **Phase 2: Data Parsing**
- Parse the Markdown files and extract the YAML front matter.
- Example:

```python
metadata = {
        'title': 'Project',
        'category': 'Data Science',
        'featured': True,
        'technologies': [
            'Python',
            'Pandas', 
            'Matplotlib'
        ],
    }

content = """
<h1> Project Overview </h1>
<p>This project is about...</p>
"""
 ``` 

### **Phase 3: Data Normalization**

```python
Project(
    slug='project-slug',
    type='data',
    title='Project Title',
    description='Project description...',
    technologies=['Python', 'Pandas', 'Matplotlib'],
    featured=True,
    content='<h1> Project Overview </h1><p>This project is about...</p>'
)
```

Then in Jinja templates, you can access the project data like this:
```jinja
{% for project in projects %}
    <div class="project">
        <h2>{{ project.title }}</h2>
        <p>{{ project.description }}</p>
        <ul>
            {% for tech in project.technologies %}
                <li>{{ tech }}</li>
            {% endfor %}
        </ul>
    </div>
{% endfor %}
```

### **Phase 4: Jinja Template Rendering**

- Script to render the Jinja templates with the normalized project data.


### **Building the Static Website**
- The final step is to build the static website by rendering the Jinja templates with the normalized project data and saving the output to the `static/` directory.


### **Phase 5: Deployment**
- Deploy the static website to a hosting service (e.g., GitHub Pages, Netlify, Vercel).


