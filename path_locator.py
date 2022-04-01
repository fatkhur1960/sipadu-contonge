import sys
from pathlib import Path
from inspect import getsourcefile


def module_path(relative_path):
    n_deep = 1

    if hasattr(sys, "frozen"):
        base_path = getattr(sys, "_MEIPASS", Path(sys.executable).parent)
        return Path(base_path).joinpath(relative_path)
    return Path(getsourcefile(lambda: 0)).parents[n_deep].absolute().joinpath(relative_path)
