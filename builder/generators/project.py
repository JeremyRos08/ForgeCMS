from .app_files import AppFilesMixin
from .base import GeneratorBase
from .project_files import ProjectFilesMixin
from .template_files import TemplateFilesMixin


class GeneratedCMSProjectGenerator(
    ProjectFilesMixin,
    AppFilesMixin,
    TemplateFilesMixin,
    GeneratorBase,
):
    """Orchestrates generation while delegating each concern to a focused module."""

    def generate(self):
        self._ensure_base()
        created = []
        created.extend(self._generate_root_files())
        created.extend(self._generate_project_package())
        created.extend(self._generate_app_package())
        created.extend(self._generate_templates())
        created.append(self._write('static/css/style.css', self._build_css()))
        return created
