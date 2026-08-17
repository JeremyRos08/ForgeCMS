from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class CodeGenerator:
    def __init__(self, template_dir: str, output_dir: str):
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.env = Environment(loader=FileSystemLoader(self.template_dir), autoescape=False)

    def render_file(self, template_name: str, output_path: str, context: dict):
        template = self.env.get_template(template_name)
        result = template.render(**context)
        final_path = self.output_dir / output_path
        final_path.parent.mkdir(parents=True, exist_ok=True)
        final_path.write_text(result, encoding='utf-8')
        return final_path

    def generate_readme(self, schema: dict):
        return self.render_file('README.md.j2', 'README.md', schema)
