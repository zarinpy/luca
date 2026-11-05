# Luca architecture

Luca is a server-rendered application. FastAPI owns HTTP. Mako renders HTML.
SQLAlchemy owns persistence. Typer replaces a Makefile as the developer
command interface. pydantic-settings loads configuration from the process
environment and `.env`.

## Repository map

| Path | Responsibility |
| --- | --- |
| `luca/app.py` | FastAPI application factory and page routes |
| `luca/cli.py` | Typer commands, including database and seed commands |
| `luca/config.py` | pydantic-settings configuration |
| `luca/database.py` | Sync engine, session, and create/drop database |
| `luca/basedata.py` | Required seed data, delegated to feature packages |
| `luca/mockup.py` | Sample seed data, delegated to feature packages |
| `luca/models.py` | Imports every model so Alembic can see it |
| `luca/templates/` | Mako templates |
| `migrations/` | Alembic environment and revision files |
| `alembic.ini` | Alembic script location and logging |

## Data commands

Base data and mockup follow one shape. The root module calls
`insert(db)` on each feature module. `db.session()` yields a SQLAlchemy
session. Callers commit inside that block. The commands are:

```text
luca db basedata insert
luca db mockup insert
```

Authentication base data inserts the built-in members. Site base data
inserts the settings row when it is missing. Authentication mockup data
inserts the sample members through the same ensure helper.

## Migrations

`luca db revision -m "..."` runs Alembic autogenerate. `migrations/env.py`
points Alembic at `Base.metadata`, compares column types and server
defaults, and does not write a file when nothing changed. A new model is
invisible until `luca/models.py` imports it.

`luca db upgrade` applies revisions. `luca db rebuild` is the destructive
local reset: drop, create, upgrade, base data, mockup.
