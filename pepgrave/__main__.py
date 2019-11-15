import argparse
import sys

import pepgrave
from pepgrave.flint import TokenTransformer, flint

pepgrave.INTERNAL_MAGIC = False


def main(argv=None):
    parser = argparse.ArgumentParser("PEPGrave")
    parser.add_argument(
        "file", nargs="?", type=argparse.FileType("r"), default=sys.stdin
    )
    namespace = parser.parse_args()
    file_contents = namespace.file.read()
    result = flint(file_contents)
    exec(compile(result, "<magic>", "exec"))


if __name__ == "__main__":
    main(sys.argv)
