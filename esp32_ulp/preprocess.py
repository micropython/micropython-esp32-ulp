from . import nocomment
from .util import split_tokens


class Preprocessor:
    def __init__(self):
        self._defines = {}

    def parse_defines(self, content):
        result = {}
        for line in content.splitlines():
            line = line.strip()
            if not line.startswith("#define"):
                # skip lines not containing #define
                continue
            line = line[8:].strip()  # remove #define
            parts = line.split(None, 1)
            if len(parts) != 2:
                # skip defines without value
                continue
            identifier, value = parts
            tmp = identifier.split('(', 1)
            if len(tmp) == 2:
                # skip parameterised defines (macros)
                continue
            value = "".join(nocomment.remove_comments(value)).strip()
            result[identifier] = value
        self._defines = result
        return result

    def expand_defines(self, line):
        found = True
        while found:  # do as many passed as needed, until nothing was replaced anymore
            found = False
            tokens = split_tokens(line)
            line = ""
            for t in tokens:
                lu = self._defines.get(t, t)
                if lu != t:
                    found = True
                line += lu

        return line

    def preprocess(self, content):
        self.parse_defines(content)
        lines = nocomment.remove_comments(content)
        result = []
        for line in lines:
            line = self.expand_defines(line)
            result.append(line)
        result = "\n".join(result)
        return result


def preprocess(content):
    return Preprocessor().preprocess(content)
