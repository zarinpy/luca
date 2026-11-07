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
| `luca/locale/` | Locale rows seeded from the supported locale codes |
| `luca/models.py` | Imports every model so Alembic can see it |
| `luca/i18n/` | Babel catalogs and the translate and compile commands |
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

Locale base data inserts one row for each supported locale code. Authentication
base data inserts the built-in members. Authentication mockup data inserts
the sample members through the same ensure helper.

## Migrations

`luca db revision -m "..."` runs Alembic autogenerate. `migrations/env.py`
points Alembic at `Base.metadata`, compares column types and server
defaults, and does not write a file when nothing changed. A new model is
invisible until `luca/models.py` imports it.

`luca db upgrade` applies revisions. `luca db rebuild` is the destructive
local reset: drop, create, upgrade, base data, mockup.

## Translations

Babel extracts messages from Python modules and Mako templates. Visible
template text uses `gettext`. Catalogs live in `luca/i18n/<locale>/LC_MESSAGES`
for `en-US`, `zh-CN`, `es-ES`, `fr-FR`, `de-DE`, `ja-JP`, `pt-BR`, `ru-RU`,
`ar-SA`, `hi-IN`, `it-IT`, `ko-KR`, `nl-NL`, `tr-TR`, `pl-PL`, `id-ID`,
`th-TH`, `vi-VN`, `fa-IR`, and `sv-SE`.

```text
luca i18n translate
luca i18n compile
```

`luca i18n translate` writes `messages.pot` and creates or updates one PO
catalog per locale. `luca i18n compile` writes the MO files the pages load.
The default locale is `en-US`.

Member text that changes by locale is stored on `MemberLocale`, not as
columns on `Member`. Each `MemberLocale` row points at one `Member` and one
`Locale`. `name` and `family` are the translated fields. An empty value falls
back to the `en-US` row.
