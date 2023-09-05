from yamale.yamale_error import YamaleError  # noqa: E402
from mockito import when, unstub  # noqa: E402
from expects import *  # noqa: F403, E402
from mamba import description, context, it  # noqa: E402
import cndprint  # noqa: E402
import cnd_io  # noqa: E402
import yaml  # noqa: E402
import src.cnd_scaffold.cnd_scaffold as cnd_scaffold


level = "Trace"
_print = cndprint.CndPrint(level=level, silent_mode=True)
provider = cnd_io.CndProviderLocalfile(creds={}, print=_print)
_cnd_io = cnd_io.CndIO(provider, print=_print)
_cnd_io_target = cnd_io.CndIO(provider, print=_print)
source = {
    'project_id': 'tests/demo',
    'definition': 'org-demo1_product1',
    'branch': 'main',
}
target = {
    'project_id': 'tests/demo-result',
    'folder': 'home',
    'branch': 'main',
}
data_to_replace = {
    'env': ['alpha', 'gamma'],
    'client': [{'name': 'A', 'token': 'B'}, {'name': 'C', 'token': 'D'}],
    'app': 'beta',
    'abc': 'def',
    'yaml': {
        'abc': 'def',
        'ghi': ['jkl', 'lmo']
    }
}
with description("CndScaffold") as self:
    with before.each:
        unstub()
        self.cnd_scaffold = cnd_scaffold.CndScaffold(source, target, data_to_replace, _cnd_io, print=_print)

    with context("__init__"):
        with it("should init the print in the class"):
            expect(self.cnd_scaffold._print).to(equal(_print))

with description("CndScaffold") as self:
    with before.each:
        unstub()
        self.cnd_scaffold = cnd_scaffold.CndScaffold(source, target, data_to_replace, _cnd_io, print=_print, cnd_io_target=_cnd_io_target)

    with context("__init__"):
        with it("should init the print in the class"):
            expect(self.cnd_scaffold._print).to(equal(_print))

    with context("_pull_file"):
        with it("should init the print in the class"):
            when(self.cnd_scaffold._cnd_io).pull_file(...).thenReturn(True)
            expect(self.cnd_scaffold._pull_file('project_id', 'filename', 'branch')).to(equal(True))

    with context("_commit_file"):
        with it("should init the print in the class"):
            when(self.cnd_scaffold._cnd_io_target).commit_file(...).thenReturn(True)
            expect(self.cnd_scaffold._commit_file('project_id', 'filename', 'content', 'branch')).to(equal(True))

    with context("_load_schema"):
        with it("should return the scheme if scheme is ok"):
            content = provider.pull_file('tests/demo', 'schema.yml')
            result = self.cnd_scaffold._load_schema()
            expect(result).to(equal(content))

        with it("should raise an error if scheme is not ok"):
            when(self.cnd_scaffold._cnd_io).pull_file(...).thenReturn(False)
            expect(lambda: self.cnd_scaffold._load_schema()).to(raise_error(NameError))

    with context("_load_structure"):
        with it("should return the structure if structure is ok"):
            content = provider.pull_file('tests/demo', 'org-demo1_product1.yml')
            result = self.cnd_scaffold._load_structure()
            expect(result).to(equal(content))

        with it("should raise an error if structure is not ok"):
            when(self.cnd_scaffold._cnd_io).pull_file(...).thenReturn(False)
            expect(lambda: self.cnd_scaffold._load_structure()).to(raise_error(NameError))

    with context("_validate_structure"):
        with it("should return the structure if structure is ok"):
            content = provider.pull_file('tests/data', 'yaml_structure.yml')
            result = self.cnd_scaffold._validate_structure()
            expect(result).to(equal(yaml.safe_load(content)))

    with context("_replace_default"):
        with it("should return file"):
            self.cnd_scaffold._target = target
            self.cnd_scaffold._data_to_replace = {'name': 'abc'}
            result = self.cnd_scaffold._replace_default({}, '%name%.yml', 'abc: %name%\n\np: a')
            expect(result).to(equal([{'file_name': 'abc.yml', 'file_content': 'abc: abc\np: a'}]))

        with it("should return file with repeat"):
            self.cnd_scaffold._target = target
            self.cnd_scaffold._data_to_replace = {'name': 'abc', 'mykey': ['a']}
            result = self.cnd_scaffold._replace_default({'repeat': 'mykey'}, '%name%.yml', 'abc: %name%\n\np: a')
            expect(result).to(equal([{'file_name': 'abc.yml', 'file_content': 'abc: abc\np: a'}]))

        with it("should return good content with jinja engine"):
            self.cnd_scaffold.engine = 'jinja2'
            self.cnd_scaffold._target = target
            self.cnd_scaffold._data_to_replace = {'name': 'abc'}
            result = self.cnd_scaffold._replace_default({}, '{{ name }}.yml', 'abc: {{ name }}\n\np: a')
            expect(result).to(equal([{'file_name': 'abc.yml', 'file_content': 'abc: abc\np: a'}]))

        # with it("should return good content with jinja engine and loop"):
        #     self.cnd_scaffold.engine = 'jinja2'
        #     self.cnd_scaffold._target = target
        #     self.cnd_scaffold._data_to_replace = {'clients': {'A': {'lines': {'C': 1, 'A': 2}}}, 'lines': {'C': 1, 'A': 2}}
        #     result = self.cnd_scaffold._replace_default({'repeat': 'clients'}, '{{ clients }}.yml', '{% for line in lines %}{{ line }}{% endfor %}')
        #     expect(result).to(equal([{'file_name': 'abc.yml', 'file_content': 'abc: abc\np: a'}]))

        with it("should throw error if invalid yaml"):
            self.cnd_scaffold.engine = 'jinja2'
            self.cnd_scaffold._target = target
            self.cnd_scaffold._data_to_replace = {'name': 'abc'}
            expect(lambda: self.cnd_scaffold._replace_default({}, '{{ name }}.yml', 'abc: {{ name }}\n\np: b: a')).to(raise_error(yaml.scanner.ScannerError))

    with context("_validate_structure"):
        with it("should raise an error if structure is not valid"):
            when(self.cnd_scaffold)._load_structure(...).thenReturn()
            self.cnd_scaffold.structure = '{a: b}'
            expect(lambda: self.cnd_scaffold._validate_structure()).to(raise_error(YamaleError))

    with context("_load_file"):
        with before.each:
            self.cnd_scaffold.yaml_structure = yaml.safe_load(provider.pull_file('tests/data', 'yaml_structure.yml'))
            when(self.cnd_scaffold)._pull_file(...).thenReturn('')

        with it("should load and prepare file"):
            self.cnd_scaffold.engine = 'jinja2'
            when(self.cnd_scaffold)._commit_file(...).thenReturn(2)
            when(self.cnd_scaffold)._replace_default(...).thenReturn([{'file_name': 'file_name', 'file_content': 'file_content'}])
            result = self.cnd_scaffold._load_file({"name": 'abc', 'target': 'def'})
            expect(len(result)).to(equal(1))

        with it("should load and prepare file"):
            self.cnd_scaffold.engine = 'jinja2'
            when(self.cnd_scaffold)._commit_file(...).thenReturn(4)
            when(self.cnd_scaffold)._replace_default(...).thenReturn([{'file_name': 'file_name', 'file_content': 'file_content'}, {'file_name': 'file_name', 'file_content': 'file_content'}])
            result = self.cnd_scaffold._load_file({"name": 'abc'})
            expect(len(result)).to(equal(2))

        with it("should load and prepare file"):
            when(self.cnd_scaffold)._commit_file(...).thenReturn(3)
            when(self.cnd_scaffold)._replace_default(...).thenReturn([{'file_name': 'file_name', 'file_content': 'file_content'}])
            result = self.cnd_scaffold._load_file({"name": 'abc'})
            expect(len(result)).to(equal(1))

    with context("_load_file (loop)"):
        with before.each:
            self.cnd_scaffold.yaml_structure = yaml.safe_load(provider.pull_file('tests/data', 'yaml_structure.yml'))
            when(self.cnd_scaffold)._pull_file(...).thenReturn(provider.pull_file('tests/demo/org-demo1', 'product1/loop/loop.yml'))
            self.expected_result = [
                {'file_name': 'ad-A/B.yml', 'file_content': 'name: B'},
                {'file_name': 'ad-C/D.yml', 'file_content': 'name: D'}
            ]

        with it("should load and prepare file"):
            my_file = self.cnd_scaffold.yaml_structure['init'][-2]
            result = self.cnd_scaffold._load_file(my_file)
            expect(result).to(equal(self.expected_result))

        with it("should load and prepare file"):
            when(self.cnd_scaffold)._pull_file(...).thenReturn(provider.pull_file('tests/demo/org-demo1', 'product1/loop-jinja/loop.yml'))
            my_file = self.cnd_scaffold.yaml_structure['init'][-1]
            self.cnd_scaffold.engine = 'jinja2'
            result = self.cnd_scaffold._load_file(my_file)
            expect(result).to(equal(self.expected_result))

    with context("_load_files"):
        with before.each:
            self.cnd_scaffold.yaml_structure = yaml.safe_load(provider.pull_file('tests/data', 'yaml_structure.yml'))
            when(self.cnd_scaffold)._pull_file(...).thenReturn('')
            when(self.cnd_scaffold)._commit_file(...).thenReturn(5)

        with it("should load and prepare file"):
            when(self.cnd_scaffold)._load_file(...).thenReturn([{}])
            result = self.cnd_scaffold._load_files('init')
            expect(result).to(equal(7))

        with it("should raise an error if file cannot be load"):
            when(self.cnd_scaffold)._pull_file(...).thenReturn(False)
            expect(lambda: self.cnd_scaffold._load_files('init')).to(raise_error(NameError))


        with it("should skip and return 0 if nothing to push for this step"):
            expect(self.cnd_scaffold._load_files('toto')).to(equal(0))

    with context("_replace_content for jinja engine"):
        with before.each:
            self.cnd_scaffold.engine = 'jinja2'

        with it("should replace data"):
            template = "A{{ varname }}C{{ othervar}}E"
            result = self.cnd_scaffold._replace_content(template, {'varname': 'B', 'othervar': 'D'})
            expect(result).to(equal('ABCDE'))

    with context("_replace_content"):
        with before.each:
            self.cnd_scaffold.engine = 'default'

        with it("should replace when data is an array of dict"):
            result = self.cnd_scaffold._replace_content("%client.name%", {'client': data_to_replace['client'][0]})
            expect(result).to(equal('A'))

        with it("should replace"):
            result = self.cnd_scaffold._replace_content("%abc%-%app%", {})
            expect(result).to(equal(f'{data_to_replace["abc"]}-{data_to_replace["app"]}'))

        with it("should replace"):
            result = self.cnd_scaffold._replace_content("%abc%-%app%", {})
            expect(result).to(equal(f'{data_to_replace["abc"]}-{data_to_replace["app"]}'))

        with it("should replace"):
            self.cnd_scaffold._data_to_replace = {
                'app': 'beta',
            }
            result = self.cnd_scaffold._replace_content("%abc%-%app%", {})
            expect(result).to(equal(f'%abc%-{data_to_replace["app"]}'))

        with it("should replace with the local_var first"):
            result = self.cnd_scaffold._replace_content("%abc%-", {'abc': 'me-first'})
            expect(result).to(equal(f'me-first-'))

        with it("should replace with the local_var first"):
            result = self.cnd_scaffold._replace_content("a: %env%", {})
            expect(result).to(equal('a: ["alpha", "gamma"]'))

    with context("_push_files"):
        with it("should push files"):
            when(self.cnd_scaffold._cnd_io).push_files(...).thenReturn(True)
            result = self.cnd_scaffold._push_files()
            expect(result).to(equal(True))

        with it("should raise an error if push failed"):
            when(self.cnd_scaffold._cnd_io_target).push_files(...).thenReturn(False)
            expect(lambda: self.cnd_scaffold._push_files()).to(raise_error(NameError))

    with context("_apply_step"):
        with before.each:
            when(self.cnd_scaffold)._validate_structure(...).thenReturn()
            when(self.cnd_scaffold)._load_files(...).thenReturn()

        with it("should return True if everything work"):
            when(self.cnd_scaffold)._push_files(...).thenReturn(True)
            result = self.cnd_scaffold._apply_step('')
            expect(result).to(equal(True))

        with it("should raise an error if push failed"):
            when(self.cnd_scaffold)._push_files(...).thenRaise(NameError)
            expect(lambda: self.cnd_scaffold._apply_step('')).to(raise_error(NameError))

    with context("init"):
        with it("should return True if everything work"):
            when(self.cnd_scaffold)._apply_step(...).thenReturn(True)
            result = self.cnd_scaffold.init()
            expect(result).to(equal(True))

        with it("should raise an error if push failed"):
            when(self.cnd_scaffold)._apply_step(...).thenRaise(NameError)
            expect(lambda: self.cnd_scaffold.init()).to(raise_error(NameError))

    with context("build"):
        with it("should return True if everything work"):
            when(self.cnd_scaffold)._apply_step(...).thenReturn(True)
            result = self.cnd_scaffold.build()
            expect(result).to(equal(True))

        with it("should raise an error if push failed"):
            when(self.cnd_scaffold)._apply_step(...).thenRaise(NameError)
            expect(lambda: self.cnd_scaffold.build()).to(raise_error(NameError))

    with context("runtime"):
        with it("should return True if everything work"):
            when(self.cnd_scaffold)._apply_step(...).thenReturn(True)
            result = self.cnd_scaffold.runtime()
            expect(result).to(equal(True))

        with it("should raise an error if push failed"):
            when(self.cnd_scaffold)._apply_step(...).thenRaise(NameError)
            expect(lambda: self.cnd_scaffold.runtime()).to(raise_error(NameError))

    with context("_default_replace_engine"):
        with before.each:
            f = open("tests/demo/org-demo1/product1/loop/loop.yml", "r")
            self.client_file = f.read()

        with it("should replace string"):
            result = self.cnd_scaffold._default_replace_engine(self.client_file, {"client.token": 'Name'})
            expect(result).to(equal('name: Name\n'))

        with it("should replace string"):
            result = self.cnd_scaffold._default_replace_engine(self.client_file, {"client.token": ['Na', 'me']})
            expect(result).to(equal('name: Na,me\n'))

        with it("should replace string"):
            result = self.cnd_scaffold._default_replace_engine(self.client_file, {"client": {'token': 'Name'}})
            expect(result).to(equal('name: Name\n'))

        with it("should replace string"):
            result = self.cnd_scaffold._default_replace_engine(self.client_file, {"client": {'token': ['Na', 'me']}})
            expect(result).to(equal('name: Na,me\n'))
