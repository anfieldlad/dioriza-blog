# Bobby Dioriza

A personal Hugo blog for yearly movie and series reviews, trip itineraries, and a few personal notes.

## Stack

- [Hugo](https://gohugo.io/)
- Custom layouts in `layouts/`
- Custom styling in `static/css/site.css`
- WordPress import script in `scripts/import_wordpress.py`

## Content Structure

- `content/reviews/` for yearly movies and series posts
- `content/itineraries/` for trip plans and travel notes
- `content/thoughts/` for essays and personal writing
- `content/pages/` for standalone pages such as About

## Run Locally

Install Hugo Extended first, then run from the project root:

```powershell
hugo server --buildDrafts --disableFastRender
```

Open the local URL shown by Hugo, usually [http://localhost:1313](http://localhost:1313).

If you use the local Hugo binary stored in this repo, run:

```powershell
.\tools\hugo\hugo.exe server --buildDrafts --disableFastRender
```

## Create New Posts

Examples:

```powershell
hugo new reviews/2026-movies-series.md
hugo new itineraries/seoul-2026.md
hugo new thoughts/my-new-note.md
```

## WordPress Import

This repo includes a small importer for WordPress XML exports.

Example:

```powershell
python .\scripts\import_wordpress.py .\your-wordpress-export.xml --copy-source
```

What it does:

- imports published posts and pages
- maps WordPress categories into Hugo sections
- preserves HTML content for posts that rely on rich formatting
- carries categories and tags into Hugo front matter
- supports yearly review and destination-based organization

## Deployment

A separate deployment guide for Vercel is available here:

- [docs-vercel-deploy.md](./docs-vercel-deploy.md)

## Notes

- The site uses a fully custom Hugo setup, not an external theme.
- HTML rendering is enabled in `hugo.toml` because some imported content still uses HTML.
- `public/` is ignored and should not be committed.
