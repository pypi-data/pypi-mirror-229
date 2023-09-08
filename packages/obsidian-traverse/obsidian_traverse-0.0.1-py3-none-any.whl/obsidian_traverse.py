#!/usr/bin/env python3

__prog__ = "obsidian-traverse"
__version__ = "0.0.1"
__author__ = "Layerex"
__desc__ = "Recursively list all files linked by Obsidian note."

import argparse
import os
import re

from itertools import chain
from glob import iglob
from typing import Iterable


def main():
    parser = argparse.ArgumentParser(prog=__prog__, description=__desc__)
    parser.add_argument(
        "notes",
        metavar="NOTES",
        help="Notes to traverse",
        type=note_filename,
        nargs="+",
    )
    parser.add_argument("-d", "--directory", help="Vault directory", type=str, required=True)
    parser.add_argument(
        "--abspath", help="Output absolute paths of linked files", action="store_true"
    )
    args = parser.parse_args()

    os.chdir(args.directory)
    for path in args.notes:
        for path in linked_files(os.path.relpath(path)):
            if args.abspath:
                path = os.path.abspath(path)
            print(path)


def note_filename(filename: str) -> str:
    if not is_note_filename(filename):
        raise ValueError("Note filenames must end with .md")
    return filename


def is_note_filename(filename: str) -> bool:
    return filename.endswith(".md")


LINK_REGEX = re.compile(r"!?\[\[([^#|\||\^|\]|\n]+)")
visited = {}


def linked_files(filename: str) -> Iterable[str]:
    yield filename
    with open(filename) as f:
        for match in re.findall(LINK_REGEX, f.read()):
            basename, ext = os.path.splitext(match)
            traversable = False
            if ext == "":
                match += ".md"
                traversable = True
            path = note_path(match)
            if traversable:
                if path and path not in visited:
                    visited[path] = True
                    for path in linked_files(path):
                        yield path
            else:
                yield path


def note_path(filename: str) -> str:
    try:
        return next(iglob(f"**/{filename}.md"))
    except StopIteration:
        try:
            return next(iglob(f"**/{filename}"))
        except StopIteration:
            return None


if __name__ == "__main__":
    main()
