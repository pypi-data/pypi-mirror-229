from mockito import when, unstub  # noqa: E402
from expects import *  # noqa: F403, E402
from mamba import description, context, it  # noqa: E402
import yaml  # noqa: E402
import src.cnd_scaffold as scaffold
import tests.vars as vars


with description("File") as self:
    with before.each:
        unstub()
        self.tested_instance = scaffold.file.File(vars._print)

    with context("__init__"):
        with it("should init the print in the class"):
            expect(self.tested_instance._print).to(equal(vars._print))

    with context("apply single file"):
        with before.each:
            self.expected = vars.read_yaml_file('tests/data/single_file/expected.yml')
            source = vars.read_yaml_file('tests/data/single_file/source.yml')
            self.file_name, self.file_content = self.tested_instance.apply(source["file_name"], source["file_content"], source["data"])

        with it("should init the print in the class"):
            expect(self.file_name).to(equal(self.expected["file_name"]))

        with it("should init the print in the class"):
            expect(self.file_content).to(equal(self.expected["file_content"]))

    with context("apply single file with loop"):
        with before.each:
            self.expected = vars.read_yaml_file('tests/data/single_file_loop/expected.yml')
            source = vars.read_yaml_file('tests/data/single_file_loop/source.yml')
            self.file_name, self.file_content = self.tested_instance.apply(source["file_name"], source["file_content"], source["data"])

        with it("should init the print in the class"):
            expect(self.file_name).to(equal(self.expected["file_name"]))

        with it("should init the print in the class"):
            expect(self.file_content).to(equal(self.expected["file_content"]))

    with context("apply single file with loop"):
        with before.each:
            self.expected = vars.read_yaml_file('tests/data/single_file_loop_advanced/expected.yml')
            source = vars.read_yaml_file('tests/data/single_file_loop_advanced/source.yml')
            self.file_name, self.file_content = self.tested_instance.apply(source["file_name"], source["file_content"], source["data"])

        with it("should init the print in the class"):
            expect(self.file_name).to(equal(self.expected["file_name"]))

        with it("should init the print in the class"):
            expect(self.file_content).to(equal(self.expected["file_content"]))