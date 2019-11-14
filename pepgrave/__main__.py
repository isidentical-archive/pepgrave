import argparse
import sys

import pepgrave
from pepgrave.magic import fix_file

pepgrave.INTERNAL_MAGIC = False


def main(argv=None):
    parser = argparse.ArgumentParser("PEPGrave")
    parser.add_argument(
        "file", nargs="?", type=argparse.FileType("r"), default=sys.stdin
    )
    namespace = parser.parse_args()
    result = fix_file(namespace.file)
    exec(compile(result, "<magic>", "exec"))


if __name__ == "__main__":
    main(sys.argv)
