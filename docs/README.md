# Aaron's test of docs

steps:

- install packages (I used conda, but we'd use pip/vm): `conda install mkdocs mkdocs-material mkdocstrings mkdocstrings-python`
- from repo root : `mkdocs new . `.  This created the `docs/` dir and `mydocs.yml` file
- I updated `mydocs.yml` as suggested by ChatGPT
- I created  `api.md` (should be populated by mkdocs) and `getting-started.md` (can be human created) as suggested by ChatGPT
- as a test, I am only producing API docs for `vatican_scraper.step05_add_to_database` (in the `api.md` file)
- test with `mkdocs serve`
- can build the (static) site with `mkdocs build`, but prior to this should add `site/` to the `.gitignore`.  Later we can set up the github.io site to host these files.