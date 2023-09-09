import pathlib
import argparse
from datetime import datetime
from typing import Optional

from .ide_launcher import launch_ide
from .template import READMEMarkdownTemplate, LicenceTemplate
from .template.bolt_py import GitIgnorePyTemplate, SetupPyTemplate


def create_python_project(
        proj_name: str,
        author: str,
        parent_dir: str = ".",
        is_pypi_proj: bool = False,
        is_git_proj: bool = False,
        ide: Optional[str] = None,
):
    """
    创建一个 Python 项目并用指定的 IDE 打开。

    :param proj_name: (str) 项目名称
    :param author: (str) 项目作者
    :param parent_dir: (str) 项目所在的父目录, 默认为当前目录
    :param is_git_proj: (bool) 是否是一个 Git 项目, 默认为 False
    :param is_pypi_proj: (bool) 是否是一个 PyPI 项目, 默认为 False
    :param ide: (Optional[str]) 要打开的 IDE, 默认为 None, 即不打开 IDE
    """
    # 创建项目目录, 若已存在则报错
    proj_path = pathlib.Path(parent_dir) / proj_name
    proj_path.mkdir(parents=True, exist_ok=False)  # 创建项目文件夹

    try:
        # 使用模板文件创建和写入文件
        (proj_path / 'README.md').write_text(READMEMarkdownTemplate.render(project_name=proj_name))
        (proj_path / 'requirements.txt').touch()

        # 如果 is_pypi_proj 为 True
        if is_pypi_proj:
            # 从模板中创建 PyPI 项目所需文件
            (proj_path / 'setup.py').write_text(SetupPyTemplate.render(project_name=proj_name))
            (proj_path / 'MANIFEST.in').touch()

            (proj_path / 'LICENSE').write_text(LicenceTemplate.render(author=author, year=datetime.now().year))

            pkg_path = proj_path / proj_name
            pkg_path.mkdir(parents=True, exist_ok=True)

            (pkg_path / '__init__.py').touch()

        # 如果 is_git_proj 为 True
        if is_git_proj:
            # 创建 Git 项目所需文件
            (proj_path / '.gitignore').write_text(GitIgnorePyTemplate.render())

        # 如果指定了 IDE
        if ide is not None:
            launch_ide(ide=ide, project_path=proj_path.absolute().as_posix())
    except Exception as e:
        # 如果出错, 则删除项目目录
        proj_path.rmdir()
        raise e


def query_user_for_input(prompt: str, default: Optional[str] = None) -> str:
    """
    Query the user for input with a default value.

    :param prompt: The prompt to display to the user.
    :param default: The default value to use if the user doesn't provide input.
    :return: The user's input or the default value.
    """
    user_input = input(f"{prompt} [{'default: ' + default if default else ''}] > ").strip()
    return user_input or default


def main():
    parser = argparse.ArgumentParser(description='Create a Python project and open it in a specified IDE.')

    parser.add_argument('-n', metavar='PROJECT_NAME', help='Name of the project.')
    parser.add_argument('-p', '--parent-dir', default=None, help='Parent directory where the project will be created. Defaults to the current directory.')
    parser.add_argument('--pypi', action='store_true', default=None, help='Specify if it\'s a PyPI project. If set, appropriate setup files will be generated.')
    parser.add_argument('--git', action='store_true', default=None, help='Specify if it\'s a Git project. If set, a git repository will be initialized.')
    parser.add_argument('--ide', choices=['pycharm', 'vscode'], help='The IDE to open the project in. Currently, only PyCharm and VSCode are supported.')
    parser.add_argument("--author", metavar="AUTHOR", default=None, help="The author of the project.")

    args = parser.parse_args()

    if not args.n:
        args.n = query_user_for_input("Please enter the project name:")

    if not args.author:
        args.author = query_user_for_input("Please enter the author name:")

    if args.parent_dir is None:
        args.parent_dir = query_user_for_input("Please enter the parent directory for the project:", ".")

    if args.pypi is None:
        args.pypi = query_user_for_input("Is it a PyPI project? (y/n):", "n").lower() == 'y'

    if args.git is None:
        args.git = query_user_for_input("Is it a Git project? (y/n):", "n").lower() == 'y'

    if args.ide is None:
        args.ide = query_user_for_input("Which IDE do you want to use (pycharm/vscode)?", "pycharm")

    create_python_project(
        ide=args.ide,
        proj_name=args.n,
        is_git_proj=args.git,
        is_pypi_proj=args.pypi,
        parent_dir=args.parent_dir,
        author=args.author,
    )
