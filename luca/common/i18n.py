"""Translated fields stored on a separate row for each locale."""

from luca.i18n import DEFAULT_CODE

TEXT_FIELDS = ("name", "family")


def _row(rows: object, code: str) -> object | None:
    for row in rows:
        if row.locale.code == code:
            return row
    return None


def pick(entity: object, field: str, code: str = DEFAULT_CODE) -> str:
    """Return one translated field, falling back to en-US when empty."""
    rows = entity.translations
    selected = _row(rows, code)
    if selected is not None:
        value = getattr(selected, field) or ""
        if value:
            return value
    if code == DEFAULT_CODE:
        return ""
    fallback = _row(rows, DEFAULT_CODE)
    if fallback is None:
        return ""
    return getattr(fallback, field) or ""


def full_name(entity: object, code: str = DEFAULT_CODE) -> str:
    """Join the given name and family for `code`."""
    parts = []
    for field in TEXT_FIELDS:
        value = pick(entity, field, code)
        if value:
            parts.append(value)
    return " ".join(parts)
