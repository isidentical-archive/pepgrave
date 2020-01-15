import ast
import tokenize
from contextlib import ExitStack, contextmanager, suppress
from dataclasses import dataclass
from typing import FrozenSet

from pepgrave import INTERNAL_MAGIC
from pepgrave.flint import flint
from pepgrave.pep import PEP


@dataclass(unsafe_hash=True)
class Magic(ExitStack):
    peps: FrozenSet[PEP]

    def __init__(self, *peps):
        self.peps = frozenset(PEP.from_id_seq(peps))
        super().__init__()

    def __enter__(self):
        super().__enter__()
        for pep in self.peps:
            for exception in pep.suppresses:
                self.enter_context(suppress(exception))


@contextmanager
def disable():
    yield


def fix_file(f):
    source = f.read()
    tree = flint(source)
    ast.fix_missing_locations(tree)
    f.close()
    return tree


def __internal_magic():
    main = __import__("__main__")
    main_tree = fix_file(open(main.__file__))
    exec(compile(main_tree, main.__file__, "exec"), main.__dict__)
    exit()

if INTERNAL_MAGIC:
    __internal_magic()
