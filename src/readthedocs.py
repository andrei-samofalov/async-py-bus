import os
from pathlib import Path
from typing import AnyStr

current_dir = Path(__file__).resolve().parent

if current_dir.name == 'src':
    current_dir = current_dir.parent

examples_dir = current_dir / "src/examples"
direction_dir = current_dir / "src/docs/examples"


def git_add():
    """Add new files to git"""
    os.system(f"git add {direction_dir}")


def read(name: Path) -> AnyStr:
    """Reads the content of doc file"""
    with name.open("r") as f:
        return f.read()


def make_markdown(doc: AnyStr) -> AnyStr:
    """Make markdown doc format"""
    return f"```python\n{doc}\n```"


def record(name: str, content: str):
    """Record the content of doc file"""
    file = Path(direction_dir / f"{name.removesuffix('.py')}.md")
    dir_path = file.parent

    dir_path.mkdir(exist_ok=True)
    with file.open("w") as f:
        f.write(content)

    return 1


def skip_file(file_name: AnyStr) -> bool:
    """Check if a file should be skipped"""
    return file_name == '__init__.py' or '__pycache__' in file_name or ".md" in file_name


def cli(dir_path: Path, recorded=0):
    """CLI command readdocs"""
    file: Path
    for file in dir_path.iterdir():
        if skip_file(file.name):
            continue

        if file.is_dir():
            return cli(file, recorded)

        content = read(file)
        dir_name = f"{dir_path.name}/" if dir_path is not examples_dir else ''
        recorded += record(f"{dir_name}{file.name}", make_markdown(content))

    print(f'Recorded: {recorded} files')

def main():
    cli(examples_dir)
    git_add()


if __name__ == '__main__':
    main()
