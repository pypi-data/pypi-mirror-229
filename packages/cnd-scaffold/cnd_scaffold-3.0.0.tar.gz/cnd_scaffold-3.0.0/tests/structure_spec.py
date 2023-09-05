from yamale.yamale_error import YamaleError  # noqa: E402
from mockito import when, unstub  # noqa: E402
from expects import *  # noqa: F403, E402
from mamba import description, context, it  # noqa: E402
import yaml  # noqa: E402
import src.cnd_scaffold as scaffold
import tests.vars as vars


project = {}
definition = {}

with description("Structure with provider") as self:
    with context("__init__"):
        with it("should init the print in the class"):
            unstub()
            self.tested_instance = scaffold.structure.Structure(project, definition, vars._print, provider="A")
            expect(self.tested_instance._provider).to(equal("A"))

with description("Structure") as self:
    with before.each:
        unstub()
        self.tested_instance = scaffold.structure.Structure(project, definition, vars._print)

    with context("__init__"):
        with it("should init the print in the class"):
            expect(self.tested_instance._print).to(equal(vars._print))

    with context("structure getter"):
        with it("should return structure value"):
            when(self.tested_instance._cnd_io).pull_file(...).thenReturn('A')
            expect(self.tested_instance.structure).to(equal('A'))

        with it("should generate an error"):
            when(self.tested_instance._cnd_io).pull_file(...).thenReturn(False)
            expect(lambda: self.tested_instance.structure).to(raise_error(NameError))

    with context("schema getter"):
        with it("should return schema value"):
            when(self.tested_instance._cnd_io).pull_file(...).thenReturn('A')
            expect(self.tested_instance.schema).to(equal('A'))

        with it("should generate an error"):
            when(self.tested_instance._cnd_io).pull_file(...).thenReturn(False)
            expect(lambda: self.tested_instance.schema).to(raise_error(NameError))

    with context("files getter"):
        with it("should return schema value"):
            self.tested_instance._structure = vars.read_file('tests/data/structure/structure.yml')
            expected = vars.read_yaml_file('tests/data/structure/expected.yml')
            when(self.tested_instance._cnd_io).pull_file(...).thenReturn("A").thenReturn("B").thenReturn("C")
            expect(self.tested_instance.files).to(equal(expected))

        with it("should return cached value"):
            self.tested_instance._files = 'ABA'
            expect(self.tested_instance.files).to(equal('ABA'))

    with context("_validate"):
        with it("should return true"):
            self.tested_instance._schema = vars.read_file('tests/data/structure/schema.yml')
            self.tested_instance._structure = vars.read_file('tests/data/structure/structure.yml')
            result = self.tested_instance._validate()
            expect(result).to(equal(True))

        with it("should raise an error"):
            self.tested_instance._schema = vars.read_file('tests/data/structure/schema.yml')
            self.tested_instance._structure = vars.read_file('tests/data/structure/bad_structure.yml')
            expect(lambda: self.tested_instance._validate()).to(raise_error(NameError))   

    with context("get"):
        with it("should return file"):
            files = vars.read_yaml_file('tests/data/structure/expected.yml')
            self.tested_instance._files = files
            when(self.tested_instance)._validate(...).thenReturn(True)
            expect(self.tested_instance.get()).to(equal(files))        