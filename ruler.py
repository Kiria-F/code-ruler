import sys, os, mimetypes

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

        path: str
        files: list[FileInfo]
        lines = lambda self: sum(f.lines for f in self.files)

    dirs: list[DirInfo] = []
    lines = lambda self: sum(d.lines() for d in self.dirs)


def main():
    if len(sys.argv) < 2:
        print('Counts lines of code (actually any text files) in a selected directory.')
        print(f'Usage: python {os.path.basename(__file__)} <path> [exclude]...')
        print(f'Example: python {os.path.basename(__file__)} {os.sep}{os.path.join("Users", "u", "Code", "some-project")} {os.sep}venv {os.sep}.git {os.sep}.vscode __pycache__')
        return
    exclude_paths = sys.argv[2:]
    root_path = sys.argv[1]
    tree_info = TreeInfo()
    for location, dirs, files in os.walk(root_path):
        rel_location = location[len(root_path):]
        if any(rel_location.startswith(exclude_path) if exclude_path.startswith(os.sep) else exclude_path in rel_location for exclude_path in exclude_paths):
            continue
        dir_info = TreeInfo.DirInfo(rel_location)
        for file in files:
            file_type = mimetypes.guess_type(file)[0]
            if file_type is not None and file_type.startswith('text'):
                with open(os.path.join(location, file)) as f:
                    file_lines = len(f.readlines())
                    dir_info.files.append(TreeInfo.DirInfo.FileInfo(file, file_lines))
        if len(dir_info.files) > 0:
            tree_info.dirs.append(dir_info)

    total_lines = tree_info.lines()
    tree_info.dirs.sort(key=lambda d: d.lines(), reverse=True)
    if len(tree_info.dirs) > 0:
        for dir_info in tree_info.dirs:
            dir_lines = dir_info.lines()
            dir_lines_percent = dir_lines * 100 // total_lines
            if dir_lines_percent:
                dir_info.files.sort(key=lambda f: f.lines, reverse=True)
                print(f'{dir_info.path}: {dir_lines} ({dir_lines_percent}%)')
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
