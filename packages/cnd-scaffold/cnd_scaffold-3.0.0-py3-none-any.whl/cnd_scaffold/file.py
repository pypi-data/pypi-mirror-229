import jinja2
from .__version__ import (__version__)  # noqa: F401


class File:
    def __init__(self, _print):
        self._print = _print
        self._print.log_d(f"File Class ({__version__})")

    def _jinja_replace(self, content, data):
        environment = jinja2.Environment()
        template = environment.from_string(content)
        return template.render(data)

    def apply(self, file_name, file_content, data):
        _file_name = self._jinja_replace(file_name, data)
        _file_content = self._jinja_replace(file_content, data)
        return _file_name, _file_content