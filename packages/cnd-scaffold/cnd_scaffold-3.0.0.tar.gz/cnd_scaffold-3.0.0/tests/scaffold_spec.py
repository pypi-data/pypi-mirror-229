from yamale.yamale_error import YamaleError  # noqa: E402
from mockito import when, unstub  # noqa: E402
from expects import *  # noqa: F403, E402
from mamba import description, context, it  # noqa: E402
import yaml  # noqa: E402
import src.cnd_scaffold.scaffold as scaffold
import tests.vars as vars
import cnd_io


with description("CndScaffold") as self:
    with before.each:
        unstub()
        self.tested_instance = scaffold.Scaffold(vars._print)

    with context("__init__"):
        with it("should init the print in the class"):
            expect(self.tested_instance._print).to(equal(vars._print))

    with context("update_step"):
        with it("should update the step"):
            new_step = ['A', 'B']
            self.tested_instance.update_step(new_step)
            expect(self.tested_instance.step).to(equal(new_step))

    with context("_commit_files"):
        with before.each:
            files = vars.read_yaml_file('tests/data/apply_repeat/expected.yml')
            self.tested_instance._cnd_io = vars._cnd_io
            self.result = self.tested_instance._commit_files(files, "project", "main")

        with it("should update commit list"):
            expect(self.result).to(equal(True))

        with it("should update commit list"):
            expect(len(self.tested_instance._cnd_io._files["project"]["main"])).to(equal(2))

    with context("_commit_files"):
        with it("should return an instance of cnd_io"):
            _provider = cnd_io.CndProviderLocalfile(creds={}, print=vars._print)
            _cnd_io = self.tested_instance._get_cnd_io(_provider)
            expect(isinstance(_cnd_io, cnd_io.CndIO)).to(equal(True))

        with it("should return an instance of cnd_io if provider is not provide"):
            _cnd_io = self.tested_instance._get_cnd_io(None)
            expect(isinstance(_cnd_io, cnd_io.CndIO)).to(equal(True))

    with context("apply single file"):
        with it("should generate file"):
            expected = vars.read_yaml_file('tests/data/apply/expected.yml')
            source = vars.read_yaml_file('tests/data/apply/source.yml')
            files = self.tested_instance.apply('init', source["model_files"], source["data"])
            expect(files).to(equal(expected))

        with it("should generate multiple file"):
            expected = vars.read_yaml_file('tests/data/apply_multiple/expected.yml')
            source = vars.read_yaml_file('tests/data/apply_multiple/source.yml')
            files = self.tested_instance.apply('init', source["model_files"], source["data"])
            expect(files).to(equal(expected))

        with it("should  repeat file"):
            expected = vars.read_yaml_file('tests/data/apply_repeat/expected.yml')
            source = vars.read_yaml_file('tests/data/apply_repeat/source.yml')
            files = self.tested_instance.apply('init', source["model_files"], source["data"])
            expect(files).to(equal(expected))