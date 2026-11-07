"""Babel message catalogs for Luca's locales."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from babel import Locale
from babel.core import UnknownLocaleError
from babel.messages.catalog import Catalog
from babel.messages.extract import extract_from_dir
from babel.messages.frontend import parse_mapping_cfg
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po, write_po
from babel.support import NullTranslations, Translations
from babel.util import LOCALTZ

from luca.manifest import __appname__, __version__

DOMAIN = "messages"
WIDTH = 76
PACKAGE_DIR = Path(__file__).resolve().parents[1]
CATALOG_DIR = Path(__file__).resolve().parent
MAPPING_FILE = CATALOG_DIR / "babel.cfg"
TEMPLATE_NAME = "messages.pot"

# Language name, locale code. Codes are the directory names under luca/i18n.
LOCALES: tuple[tuple[str, str], ...] = (
    ("English (United States)", "en-US"),
    ("Chinese (Simplified)", "zh-CN"),
    ("Spanish (Spain)", "es-ES"),
    ("French (France)", "fr-FR"),
    ("German (Germany)", "de-DE"),
    ("Japanese (Japan)", "ja-JP"),
    ("Portuguese (Brazil)", "pt-BR"),
    ("Russian (Russia)", "ru-RU"),
    ("Arabic (Saudi Arabia)", "ar-SA"),
    ("Hindi (India)", "hi-IN"),
    ("Italian (Italy)", "it-IT"),
    ("Korean (South Korea)", "ko-KR"),
    ("Dutch (Netherlands)", "nl-NL"),
    ("Turkish (Turkey)", "tr-TR"),
    ("Polish (Poland)", "pl-PL"),
    ("Indonesian (Indonesia)", "id-ID"),
    ("Thai (Thailand)", "th-TH"),
    ("Vietnamese (Vietnam)", "vi-VN"),
    ("Persian (Iran)", "fa-IR"),
    ("Swedish (Sweden)", "sv-SE"),
)
DEFAULT_CODE = LOCALES[0][1]


class CatalogError(Exception):
    """A catalog command cannot read or write a locale."""


@dataclass(frozen=True)
class TranslateResult:
    """Paths written by one translate run."""

    template: Path
    initialized: tuple[str, ...]
    updated: tuple[str, ...]


def locale_codes() -> tuple[str, ...]:
    return tuple(code for _, code in LOCALES)


def gettext(message: str, code: str = DEFAULT_CODE) -> str:
    """Return the translation of `message` for `code`."""
    return translation(code).gettext(message)


def translation(
    code: str = DEFAULT_CODE,
    catalog_dir: Path | None = None,
) -> NullTranslations:
    """Load the compiled catalog for `code`, or the source strings."""
    _require_code(code)
    directory = CATALOG_DIR if catalog_dir is None else catalog_dir
    return Translations.load(directory, [code], DOMAIN)


def translate(
    *,
    source_dir: Path | None = None,
    catalog_dir: Path | None = None,
) -> TranslateResult:
    """Extract messages and create or update every locale catalog."""
    source = PACKAGE_DIR if source_dir is None else source_dir
    root = CATALOG_DIR if catalog_dir is None else catalog_dir
    template = root / TEMPLATE_NAME
    _extract(source, template)
    initialized: list[str] = []
    updated: list[str] = []
    for code in locale_codes():
        po_file = _po_path(root, code)
        if po_file.is_file():
            _update_catalog(template, po_file, code)
            updated.append(code)
        else:
            _create_catalog(template, po_file, code)
            initialized.append(code)
    return TranslateResult(
        template=template,
        initialized=tuple(initialized),
        updated=tuple(updated),
    )


def compile_catalogs(
    *,
    catalog_dir: Path | None = None,
) -> tuple[str, ...]:
    """Compile every locale catalog to an MO file."""
    root = CATALOG_DIR if catalog_dir is None else catalog_dir
    missing = [
        code
        for code in locale_codes()
        if not _po_path(root, code).is_file()
    ]
    if missing:
        message = "missing catalogs: " + ", ".join(missing)
        raise CatalogError(message)
    for code in locale_codes():
        _compile_one(root, code)
    return locale_codes()


def _require_code(code: str) -> None:
    if code not in locale_codes():
        message = f"unknown locale {code}"
        raise CatalogError(message)


def _babel_locale(code: str) -> Locale:
    _require_code(code)
    try:
        return Locale.parse(code.replace("-", "_"))
    except (UnknownLocaleError, ValueError) as exc:
        message = f"unknown locale {code}"
        raise CatalogError(message) from exc


def _po_path(root: Path, code: str) -> Path:
    return root / code / "LC_MESSAGES" / f"{DOMAIN}.po"


def _mo_path(root: Path, code: str) -> Path:
    return root / code / "LC_MESSAGES" / f"{DOMAIN}.mo"


def _load_mapping() -> tuple[
    list[tuple[str, str]],
    dict[str, dict[str, object]],
]:
    with MAPPING_FILE.open(encoding="utf-8") as handle:
        method_map, options_map = parse_mapping_cfg(
            handle,
            filename=str(MAPPING_FILE),
        )
    return method_map, options_map


def _extract(source_dir: Path, template: Path) -> None:
    if not source_dir.is_dir():
        message = f"source directory does not exist: {source_dir}"
        raise CatalogError(message)
    method_map, options_map = _load_mapping()
    catalog = Catalog(
        project=__appname__,
        version=__version__,
        copyright_holder=__appname__,
        charset="utf-8",
        domain=DOMAIN,
    )
    extracted = extract_from_dir(source_dir, method_map, options_map)
    for filename, lineno, message, comments, context in extracted:
        catalog.add(
            message,
            None,
            [(filename, lineno)],
            auto_comments=comments,
            context=context,
        )
    template.parent.mkdir(parents=True, exist_ok=True)
    with template.open("wb") as outfile:
        write_po(outfile, catalog, width=WIDTH, sort_by_file=True)


def _create_catalog(template: Path, po_file: Path, code: str) -> None:
    locale = _babel_locale(code)
    with template.open("rb") as infile:
        catalog = read_po(infile, locale=locale, domain=DOMAIN)
    catalog.locale = locale
    catalog.revision_date = datetime.now(LOCALTZ)
    catalog.fuzzy = False
    _write_catalog(po_file, catalog)


def _update_catalog(template: Path, po_file: Path, code: str) -> None:
    locale = _babel_locale(code)
    with template.open("rb") as infile:
        pot = read_po(infile, domain=DOMAIN)
    with po_file.open("rb") as infile:
        catalog = read_po(infile, locale=locale, domain=DOMAIN)
    catalog.update(pot)
    _write_catalog(po_file, catalog)


def _write_catalog(po_file: Path, catalog: Catalog) -> None:
    po_file.parent.mkdir(parents=True, exist_ok=True)
    with po_file.open("wb") as outfile:
        write_po(outfile, catalog, width=WIDTH, sort_by_file=True)


def _compile_one(root: Path, code: str) -> None:
    locale = _babel_locale(code)
    po_file = _po_path(root, code)
    with po_file.open("rb") as infile:
        catalog = read_po(infile, locale=locale, domain=DOMAIN)
    if catalog.fuzzy:
        message = f"fuzzy catalog {code}"
        raise CatalogError(message)
    mo_file = _mo_path(root, code)
    with mo_file.open("wb") as outfile:
        write_mo(outfile, catalog)
