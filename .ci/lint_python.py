#!/usr/bin/env python3
# Wrapper script to customize linting of the project with pylint:
# - provides workaround for https://github.com/PyCQA/pylint/issues/3944 (implicit namespace
#   packages within regular packages are ignored)
# - select which message types are considered as critical and contribute to non-zero exit status,
#   see also http://pylint.pycqa.org/en/latest/user_guide/run.html#exit-codes
# - explicitly specify linting targets, default rcfile and ignored directory names

import glob
import itertools
import functools
import os
import os.path
import sys
import typing

from pylint.lint import Run as RunLinter
from pylint.constants import MSG_TYPES_STATUS


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

# Include only specified message types into exit status so builds will fail only
# when there's critical enough issues found
# Set this variable to a string of short type names to select message types to be included
# (see keys from pylint.constants.MSG_TYPES for valid choices)
# Set to None to disable exit status filtering
EXIT_STATUS_MASK_STR = 'EF'

PACKAGE_MARKER = '__init__.py'
WRAPPER_EXIT_FAIL = 32  # same as for usage error in pylint


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
    filter_exit_status = EXIT_STATUS_MASK_STR is not None
    if filter_exit_status:
        try:
            include_statuses = (MSG_TYPES_STATUS[t] for t in EXIT_STATUS_MASK_STR)
            exit_status_mask = functools.reduce(int.__or__, include_statuses, 0)
        except KeyError:
            invalid_types = list(EXIT_STATUS_MASK_STR - MSG_TYPES_STATUS.keys())
            error_message = 'EXIT_STATUS_MASK_STR contains invalid message type abbreviations:'
            print(error_message, invalid_types, file=sys.stderr)
            return WRAPPER_EXIT_FAIL

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
        exit_status = runner.linter.msg_status
        if filter_exit_status:
            exit_status &= exit_status_mask
        return exit_status
    except KeyboardInterrupt:
        return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
