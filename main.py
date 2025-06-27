from __future__ import annotations

import os
import sys
from pathlib import Path
from pathspec import PathSpec


def reprint(
    *values: object,
    sep: str | None = ' ',
    end: str | None = '\n',
):
    print('\033[1G\033[1A\033[0J', end='')
    print(*values, sep=sep, end=end)


class Validator:
    empty: bool
    spec: PathSpec
    path: Path

    def __init__(self, path: Path) -> None:
        if not (path / '.gitignore').is_file():
            self.empty = True
            return
        self.empty = False
        self.path = path
        with open(path / '.gitignore') as f:
            self.spec = PathSpec.from_lines('gitwildmatch', f.readlines())

    def validate(self, path: Path) -> bool:
        if self.empty:
            return True
        rel_path = path.relative_to(self.path)
        return not self.spec.match_file(rel_path)


class FileInfo:
    path: Path
    lines_cache: int | None

    def __init__(self, path: Path) -> None:
        self.path = path
        self.lines_cache = None

    @property
    def lines(self) -> int:
        if self.lines_cache is None:
            with open(self.path) as f:
                try:
                    self.lines_cache = len(f.readlines())
                except UnicodeDecodeError:
                    self.lines_cache = 0
        return self.lines_cache

    def __str__(self) -> str:
        return self.path.name


class DirInfo:
    path: Path
    parent: DirInfo | None = None
    children: list[FileInfo | DirInfo]
    validator: Validator
    lines_cache: int | None
    scan_counter: int = 0

    def __init__(self, path: Path, parent: DirInfo | None = None) -> None:
        self.path = path
        self.children = []
        self.validator = Validator(self.path)
        self.parent = parent
        self.lines_cache = None

        for child in self.path.iterdir():
            if self.validate(child) and child.name != '.git':
                if child.is_file():
                    self.children.append(FileInfo(child))
                    DirInfo.scan_counter += 1
                    print(f'Found {DirInfo.scan_counter}', end='\r')
                elif child.is_dir():
                    self.children.append(DirInfo(child, self))

    @property
    def lines(self) -> int:
        if self.lines_cache is None:
            self.lines_cache = sum(f.lines for f in self.children)
        return self.lines_cache

    def validate(self, filename: Path) -> bool:
        if not self.validator.validate(filename):
            return False
        if self.parent is not None:
            return self.parent.validate(filename)
        return True
    
    def describe(self, level: int = 0) -> None:
        indent = '    ' * level
        print(f'{indent}{self.path.name}: {self.lines} lines {self.parent.percent(self.lines) if self.parent else "(100%)"}')
        for child in sorted(filter(lambda child: child.lines, self.children), key=lambda c: c.lines, reverse=True):
            if isinstance(child, FileInfo):
                print(f'{indent}    {child}: {child.lines} lines {self.percent(child.lines)}')
            elif isinstance(child, DirInfo):
                child.describe(level + 1)

    def percent(self, lines: int) -> str:
        percent = int(lines / self.lines * 100)
        if percent == 0:
            return '(<1%)'
        return f'({percent}%)'


def main():
    if len(sys.argv) != 2:
        print('Counts lines of code (actually any text files) in a selected directory.')
        print(f'Usage: python {os.path.basename(__file__)} <path>')
        return
    project_path = Path(sys.argv[1])
    if not project_path.is_dir():
        print(f'Error: {project_path} is not a directory')
        return
    os.chdir(project_path)
    print(f'Scanning {project_path}...')
    dir_info = DirInfo(project_path)
    print('Scan complete.\n')
    dir_info.describe()


if __name__ == '__main__':
    main()
