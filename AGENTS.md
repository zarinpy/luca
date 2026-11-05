# Luca development instructions

This is a server-rendered application. FastAPI serves HTTP and Mako renders
HTML. Typer is the command interface. Do not add a Makefile for project
commands.

## Project contract

- Read `docs/architecture.md`, `pyproject.toml`, and `luca/cli.py` before
  changing the application.
- Load configuration through `luca.config.Settings`. Do not add YAML
  settings files.
- Keep base data in feature `basedata.py` modules and register them from
  `luca/basedata.py`. Keep sample data in feature `mockup.py` modules and
  register them from `luca/mockup.py`. Both expose `insert(db)` and use
  `db.session()`.
- Put models on `luca.common.models.Base` and import them from
  `luca/models.py`.
- Create schema changes with `luca db revision -m "..."` so Alembic detects
  model changes. Do not hand-write a revision when autogenerate can see the
  change.
- Do not put credentials in source control. Local settings belong in `.env`.
