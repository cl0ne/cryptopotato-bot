#!/usr/bin/env python3

import glob
import itertools
import os
import os.path
import sys
import typing

from pylint.lint import Run as RunLinter


class DirGlob(typing.NamedTuple):
    path: str
    is_recursive: bool = False

    def get_modules(self):
        glob_parts = [self.path]
        if self.is_recursive:
            glob_parts.append('**')
        pattern = os.path.join(*glob_parts, '*.py')
        return glob.iglob(pattern, recursive=self.is_recursive)


PACKAGE_NAMES = ('devpotato_bot', 'tests')
MODULE_SEARCH_PATHS = (
    DirGlob('.'),
    DirGlob('.ci-scripts'),
    DirGlob('alembic', is_recursive=True)
)
IGNORED_DIRS = ('__pycache__', '.git')
PYLINT_RCFILE = 'pylintrc'

PACKAGE_MARKER = '__init__.py'


def is_python_file(item: os.DirEntry):
    return item.is_file() and item.name.endswith('.py')


def is_regular_package(path: str):
    marker_path = os.path.join(path, PACKAGE_MARKER)
    return os.path.isfile(marker_path)


def find_namespace_packages(package_dir: str):
    with os.scandir(package_dir) as it:
        for entry in filter(os.DirEntry.is_dir, it):
            if entry.name in IGNORED_DIRS:
                return
            path = entry.path
            if is_regular_package(path):
                yield from find_namespace_packages(path)
            else:
                yield path


def find_package_extras(packages: typing.Iterable[str]):
    # look for implicit namespace package dirs within regular packages
    # workaround for https://github.com/PyCQA/pylint/issues/3944
    for path in packages:
        if is_regular_package(path):
            yield from find_namespace_packages(path)


def find_modules(dirs: typing.Iterable[DirGlob]):
    for dir_glob in dirs:
        yield from dir_glob.get_modules()


def main(args):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    pylint_config = ['--rcfile', os.path.join(script_dir, PYLINT_RCFILE)]
    linter_args = list(itertools.chain(
        pylint_config,
        PACKAGE_NAMES,
        find_package_extras(PACKAGE_NAMES),
        find_modules(MODULE_SEARCH_PATHS),
        args
    ))
    try:
        runner = RunLinter(linter_args, exit=False)
        return runner.linter.msg_status
    except KeyboardInterrupt:
        return 64


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
