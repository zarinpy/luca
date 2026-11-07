from pathlib import Path

import pytest
from typer.testing import CliRunner

from luca.cli import app
from luca.i18n import (
    DEFAULT_CODE,
    LOCALES,
    CatalogError,
    TranslateResult,
    compile_catalogs,
    gettext,
    locale_codes,
    translate,
    translation,
)

runner = CliRunner()

EXPECTED_LOCALES = (
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


def test_locales_match_the_supported_set() -> None:
    assert LOCALES == EXPECTED_LOCALES
    assert DEFAULT_CODE == "en-US"
    assert len(set(locale_codes())) == len(LOCALES)


def test_gettext_returns_the_source_string_without_a_catalog(
    tmp_path: Path,
) -> None:
    message = "Server-rendered with FastAPI and Mako."
    assert gettext(message) == message
    assert translation("fa-IR", tmp_path).gettext(message) == message


def test_translate_extracts_updates_and_compile_loads(
    tmp_path: Path,
) -> None:
    source = tmp_path / "src"
    templates = source / "templates"
    templates.mkdir(parents=True)
    (source / "hello.py").write_text('_("Hello")\n', encoding="utf-8")
    (templates / "page.mako").write_text(
        '<p>${_("Welcome")}</p>\n',
        encoding="utf-8",
    )
    catalogs = tmp_path / "i18n"

    created = translate(source_dir=source, catalog_dir=catalogs)

    assert created.template == catalogs / "messages.pot"
    assert created.initialized == locale_codes()
    assert created.updated == ()
    pot = created.template.read_text(encoding="utf-8")
    assert 'msgid "Hello"' in pot
    assert 'msgid "Welcome"' in pot
    arabic = (catalogs / "ar-SA" / "LC_MESSAGES" / "messages.po").read_text(
        encoding="utf-8",
    )
    japanese = (
        catalogs / "ja-JP" / "LC_MESSAGES" / "messages.po"
    ).read_text(encoding="utf-8")
    chinese = (
        catalogs / "zh-CN" / "LC_MESSAGES" / "messages.po"
    ).read_text(encoding="utf-8")
    assert "nplurals=6" in arabic
    assert "nplurals=1" in japanese
    assert "Language: zh_Hans_CN" in chinese

    hello = catalogs / "fa-IR" / "LC_MESSAGES" / "messages.po"
    original = hello.read_text(encoding="utf-8")
    translated = original.replace(
        'msgid "Hello"\nmsgstr ""',
        'msgid "Hello"\nmsgstr "Salam"',
        1,
    )
    assert translated != original
    hello.write_text(translated, encoding="utf-8")
    (source / "hello.py").write_text(
        '_("Hello")\n_("Again")\n',
        encoding="utf-8",
    )

    refreshed = translate(source_dir=source, catalog_dir=catalogs)

    assert refreshed.initialized == ()
    assert refreshed.updated == locale_codes()
    merged = hello.read_text(encoding="utf-8")
    assert 'msgstr "Salam"' in merged
    assert 'msgid "Again"' in merged

    compiled = compile_catalogs(catalog_dir=catalogs)

    assert compiled == locale_codes()
    assert (catalogs / "fa-IR" / "LC_MESSAGES" / "messages.mo").is_file()
    loaded = translation("fa-IR", catalogs)
    assert loaded.gettext("Hello") == "Salam"
    assert loaded.gettext("Again") == "Again"
    assert translation("en-US", catalogs).gettext("Hello") == "Hello"


def test_translate_project_templates(tmp_path: Path) -> None:
    result = translate(catalog_dir=tmp_path)
    pot = result.template.read_text(encoding="utf-8")
    assert "Server-rendered with FastAPI and Mako." in pot
    assert (tmp_path / "en-US" / "LC_MESSAGES" / "messages.po").is_file()
    assert (tmp_path / "fa-IR" / "LC_MESSAGES" / "messages.po").is_file()


def test_compile_requires_catalogs(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="missing catalogs"):
        compile_catalogs(catalog_dir=tmp_path)


def test_unknown_locale_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="unknown locale"):
        translation("en-GB", tmp_path)


def test_cli_translate_reports_each_locale(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    template = tmp_path / "messages.pot"

    def fake_translate() -> TranslateResult:
        return TranslateResult(
            template=template,
            initialized=("en-US",),
            updated=("fa-IR",),
        )

    monkeypatch.setattr("luca.cli.translate", fake_translate)

    result = runner.invoke(app, ["i18n", "translate"])

    assert result.exit_code == 0
    assert "extracted" in result.output
    assert "initialized en-US" in result.output
    assert "updated fa-IR" in result.output


def test_cli_compile_reports_locales(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "luca.cli.compile_catalogs",
        lambda: ("en-US", "fa-IR"),
    )

    result = runner.invoke(app, ["i18n", "compile"])

    assert result.exit_code == 0
    assert "compiled en-US" in result.output
    assert "compiled fa-IR" in result.output


def test_cli_compile_reports_missing_catalogs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail() -> tuple[str, ...]:
        message = "missing catalogs: en-US"
        raise CatalogError(message)

    monkeypatch.setattr("luca.cli.compile_catalogs", fail)

    result = runner.invoke(app, ["i18n", "compile"])

    assert result.exit_code == 1
    assert "missing catalogs: en-US" in result.output
