import ast
from contextlib import ExitStack, suppress
from dataclasses import dataclass
from typing import FrozenSet

from pepgrave.flint import Flint
from pepgrave.pep import PEP


@dataclass(unsafe_hash=True)
class Magic(ExitStack):
    peps: FrozenSet[PEP]

    def __init__(self, *peps):
        self.peps = PEP.from_id_seq(peps)
        super().__init__()

    def __enter__(self):
        super().__enter__()
        for pep in self.peps:
            for exception in pep.suppresses:
                self.enter_context(suppress(exception))


def __internal_magic():
    main = __import__("__main__")
    flint = Flint()
    with open(main.__file__) as f:
        main_tree = ast.parse(f.read())
    main_tree = flint.visit(main_tree)
    ast.fix_missing_locations(main_tree)
    exec(compile(main_tree, main.__file__, "exec"), main.__dict__)
    exit()


__internal_magic()
