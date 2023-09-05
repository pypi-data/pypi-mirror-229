from .__version__ import (__version__)
from .file import File
from .structure import Structure
import cnd_io
import copy


class Scaffold:
    step = ['init', 'build', 'runtime']

    def __init__(self, _print):
        self._print = _print
        self._file = File( self._print)

    def _file_apply(self, file_name, file_content, data):
        return self._file.apply(file_name, file_content, data)

    def update_step(self, step):
        self.step = step

    def apply(self, step, model_files, data):
        result = {}
        for file in model_files:
            if step not in file['step']:
                continue
            if 'repeat' not in file:
                _file_name, _file_content = self._file_apply(file['file_name'], file['file_content'], data)
                result[_file_name] =_file_content
                continue
            for item in data[file["repeat"]]:
                sub_data = copy.deepcopy(data)
                sub_data.update(item)
                _file_name, _file_content = self._file_apply(file['file_name'], file['file_content'], sub_data)
                result[_file_name] =_file_content
        return result

    def load_model(self, project, definition, provider=None, branch="main", base_path=''):
        structure = Structure(project, definition, self._print, provider=provider, branch=branch, base_path=base_path)
        return structure.get()

    def _get_cnd_io(self, provider):
        if provider is None:
            _provider = cnd_io.CndProviderLocalfile(creds={}, print=self._print)
        else:
            _provider = provider
        return cnd_io.CndIO(_provider, print=self._print)

    def _commit_files(self, files, project, branch):
        for file_name, file_content in files.items():
            self._cnd_io.commit_file(project, file_name, file_content, branch)
        return True

    def push_files(self, files, project, provider=None, branch="main", commit_message="Pushing from CndScaffold"):
        self._cnd_io = self._get_cnd_io(provider)
        self._commit_files(files, project, branch)
        result = _cnd_io.push_files(project, commit_message=commit_message, branch=branch)
        if result is False:
            self._print.info_e(f'Cannot push content')
            self._print.trace_e(f'Content: {yaml.dump(_cnd_io._files)}')
            raise NameError(f'Content cannot be pushed')
        return True