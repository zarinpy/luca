from pathlib import Path

from mako.lookup import TemplateLookup


class MakoTemplates:
    def __init__(self, directory: Path, module_directory: Path) -> None:
        module_directory.mkdir(parents=True, exist_ok=True)
        self.lookup = TemplateLookup(
            directories=[str(directory)],
            module_directory=str(module_directory),
            input_encoding="utf-8",
            output_encoding="utf-8",
            strict_undefined=True,
        )

    def render(self, name: str, **context: object) -> str:
        rendered = self.lookup.get_template(name).render(**context)
        if isinstance(rendered, bytes):
            return rendered.decode("utf-8")
        return str(rendered)
