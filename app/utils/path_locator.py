import sys
from pathlib import Path
from inspect import getsourcefile

def module_path(relative_path):
    """
    Combine top level path location, in this project app.py folder because it serves as main/entry_point, with user relative path.

    NOTE: top_level_locator.py should be in same folder as entry_point.py(/main.py) script 
    - TEST this with executable 
    - TEST this without executable 

    NOTE: care with use of __file__ as it comes with unwarranted side effects when:
    - running from IDLE (Python shell), no __file__ attribute
    - freezers, e.g. py2exe & pyinstaller do not have __file__ attribute! 

    NOTE: care with use of sys.argv[0]
    - unexpected result when you want current module path and get path where script/executable was run from! 

    NOTE: care with use of sys.executable
    - if non-frozen application/module/script: python/path/python.exe 
    - else                                   : standalone_application_executable_name.exe
    """
    # 0 if this module next to your_entry_point.py (main.py) else += 1 for every directory deeper
    n_deep = 1

    print('sys.executable:', sys.executable)
    print('   sys.argv[0]:', Path(sys.argv[0]).parents[n_deep].absolute() / sys.argv[0])
    print('      __file__:', __file__)
    print(' getsourcefile:', Path(getsourcefile(lambda:0)).parents[n_deep].absolute())
    
    if hasattr(sys, "frozen"):
        # retreive possible longpath if needed from _MEIPASS: import win32api; 
        # sys_meipass = win32api.GetLongPathName(sys._MEIPASS)
        base_path = getattr(sys, '_MEIPASS', Path(sys.executable).parent)
        print('      _MEIPASS:', base_path)
        return Path(base_path).joinpath(relative_path)
    return Path(getsourcefile(lambda:0)).parents[n_deep].absolute().joinpath(relative_path)