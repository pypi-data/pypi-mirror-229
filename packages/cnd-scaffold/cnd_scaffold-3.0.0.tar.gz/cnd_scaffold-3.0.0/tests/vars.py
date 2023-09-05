import cndprint  # noqa: E402
import cnd_io  # noqa: E402
import yaml


level = "Trace"
silent_mode = True
_print = cndprint.CndPrint(level=level, silent_mode=silent_mode)
_provider = cnd_io.CndProviderLocalfile(creds={}, print=_print)
_cnd_io = cnd_io.CndIO(_provider, print=_print)
_cnd_io_target = cnd_io.CndIO(_provider, print=_print)


def read_file(filename):
    return open(filename).read()

def read_yaml_file(filename):
    file = read_file(filename)
    return yaml.safe_load(file)

def compare_text(result, expected):
    text1 = result.splitlines()
    text2 = expected.splitlines()
    for line in difflib.unified_diff(text1, text2, fromfile="result", tofile="expected, lineterm='"):
        _print.info_d(line)