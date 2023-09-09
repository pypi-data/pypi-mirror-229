from .launcher import *


def launch_ide(ide: str, project_path: str):
    """
    Launch the specified IDE with the specified project path

    :param ide: (str) the name of the IDE to be launched
    :param project_path: (str) the path of the project to be opened
    :return: (None)
    """
    if ide == "pycharm":
        PyCharmLauncher().launch(project_path)
    elif ide == "vscode":
        VSCodeLauncher().launch(project_path)
    else:
        raise ValueError(f"Unsupported ide: {ide}")


__all__ = ["launch_ide"]
