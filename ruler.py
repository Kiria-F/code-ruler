import os
import sys


class TreeInfo:
    class DirInfo:
        class FileInfo:
            def __init__(self, name: str, lines: int = 0) -> None:
                self.name = name
                self.lines = lines

            def __str__(self) -> str:
                return self.name

            name: str
            lines: int

        def __init__(self, path: str) -> None:
            self.path = path
            self.files = []

        def lines(self) -> int:
            return sum(f.lines for f in self.files)

        path: str
        files: list[FileInfo]

    def lines(self) -> int:
        return sum(d.lines() for d in self.dirs)

    dirs: list[DirInfo] = []


def reprint(
    *values: object,
    sep: str | None = ' ',
    end: str | None = '\n',
):
    print('\033[1G\033[1A\033[0J', end='')
    print(*values, sep=sep, end=end)


def ignored(ignore_paths: list[str], rel_location: str, file: str = '') -> bool:
    for ignore_path in ignore_paths:
        from_root = ignore_path.startswith(os.sep)
        dir_only = ignore_path.endswith(os.sep)
        rule = ignore_path.removeprefix(os.sep).removesuffix(os.sep)
        path = os.path.join(rel_location.removeprefix(os.sep), file).split(os.sep)
        if from_root:
            if dir_only:
                if len(path) > 1 and path[0] == rule:
                    return True
            else:
                if path[0] == rule:
                    return True
        else:
            if dir_only:
                if rule in path and path.index(rule) < len(path) - 1:
                    return True
            else:
                if rule in path:
                    return True
    return False


def main():
    if len(sys.argv) != 2:
        print('Counts lines of code (actually any text files) in a selected directory.')
        print(f'Usage: python {os.path.basename(__file__)} <path>')
        return
    project_path = sys.argv[1]
    project_path = project_path.removesuffix(os.sep)
    ignore_paths = ['.git/']
    if os.path.isfile(os.path.join(project_path, '.gitignore')):
        with open(os.path.join(project_path, '.gitignore')) as f:
            ignore_paths += map(lambda line: line.removesuffix('\n'), f.readlines())
    ignore_paths = list(map(lambda path: path.replace('/', os.sep), ignore_paths))
    tree_info = TreeInfo()
    files_count = 0
    print('Scanning files...')
    print('Found: 0')
    progress_line_length = 58
    for _, _, files in os.walk(project_path):
        files_count += len(files)
        reprint(f'Found: {files_count}')
    print(f'[{" " * progress_line_length}]')
    files_processed = 0
    for location, _, files in os.walk(project_path):
        rel_location = location[len(project_path) :]
        if ignored(ignore_paths, rel_location):
            continue
        dir_info = TreeInfo.DirInfo(rel_location)
        for file in files:
            if ignored(ignore_paths, rel_location, file):
                continue
            try:
                with open(os.path.join(location, file)) as f:
                    file_lines = len(f.readlines())
                    dir_info.files.append(TreeInfo.DirInfo.FileInfo(file, file_lines))
            except UnicodeDecodeError:
                continue
        if len(dir_info.files) > 0:
            tree_info.dirs.append(dir_info)
        files_processed += len(files)
        progress = files_processed * progress_line_length // files_count
        reprint(f'[{"#" * progress}{" " * (progress_line_length - progress)}]')

    print()
    total_lines = tree_info.lines()
    tree_info.dirs.sort(key=lambda d: d.lines(), reverse=True)
    if len(tree_info.dirs) > 0:
        for dir_info in tree_info.dirs:
            dir_lines = dir_info.lines()
            dir_lines_percent = dir_lines * 100 // total_lines
            if dir_lines_percent:
                dir_info.files.sort(key=lambda f: f.lines, reverse=True)
                print(f'{dir_info.path if dir_info.path else os.sep}: {dir_lines} ({dir_lines_percent}%)')
                for file_info in dir_info.files:
                    file_lines_percent = file_info.lines * 100 // dir_lines
                    if file_lines_percent:
                        print(f'    {file_info.name}: {str(file_info.lines)} ({file_lines_percent}%)')
                print()
    else:
        print('No text files found')
    print(f'Total {total_lines} lines')


if __name__ == '__main__':
    main()
