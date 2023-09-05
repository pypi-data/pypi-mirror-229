import cnd_io
import yamale
import yaml


class Structure:
    def __init__(self, project, definition, _print, provider=None, branch="main", base_path=''):
        self._print = _print
        self._project = project
        self._definition = definition
        self._branch = branch
        self._base_path = base_path
        if provider is None:
            self._provider = cnd_io.CndProviderLocalfile(creds={}, print=_print)
        else:
            self._provider = provider
        self._cnd_io = cnd_io.CndIO(self._provider, print=_print)
        self._structure = None
        self._schema = None
        self._files = None

    @property
    def structure(self):
        if self._structure is not None:
            return self._structure
        self._structure = self._cnd_io.pull_file(self._project, f'{self._base_path}{self._definition}.yml', branch=self._branch)
        if self._structure is False:
            self._print.info_e(f"Cannot found file for structure : {self._project} | {self._base_path}{self._definition}.yml")
            raise NameError('Structure unreadable')
        return self._structure

    @property
    def schema(self):
        if self._schema is not None:
            return self._schema
        self._schema = self._cnd_io.pull_file(self._project, f'{self._base_path}schema.yml', branch=self._branch)
        if self._schema is False:
            self._print.info_e(f"Cannot found file for schema : {self._project} | {self._base_path}schema.yml")
            raise NameError('Schema unreadable')
        return self._schema

    @property
    def files(self):
        if self._files is not None:
            return self._files
        result = []
        safe_structure = yaml.safe_load(self.structure)
        for file in safe_structure['files']:
            folder = "/".join([self._base_path, safe_structure["source_folder"]]).replace('//','/')
            if folder[0] == '/':
                folder = folder[1:]
            file_content = self._cnd_io.pull_file(self._project, f'{folder}/{file["name"]}', branch=self._branch)
            data = {
                "file_name": file["target"] if "target" in file else file["name"],
                "file_content": file_content,
                "step": file["step"]
            }
            if 'repeat' in file:
                data['repeat'] = file['repeat']
            result.append(data)
        return result

    def _validate(self):
        schema = yamale.make_schema(content=self.schema)
        data = yamale.make_data(content=self.structure)
        try:
            yamale.validate(schema, data)
            return True
        except ValueError as e:
            raise NameError('Validation failed')

    def get(self):
        self._validate()
        return self.files