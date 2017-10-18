
from cx_Freeze import setup, Executable
import os
os.environ['TCL_LIBRARY'] = r'C:\Users\NOA\AppData\Local\Programs\Python\Python36-32\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\NOA\AppData\Local\Programs\Python\Python36-32\tcl\tk8.6'


base = None


executables = [Executable("C:/Users/NOA/fMRI_E_Project/BarFeedback/main.py", base=base)]

includes = ["OpenGL"]
packages = ["idna", "OpenGL", "numpy"]
options = {
    'build_exe': {

        'packages':packages,
        'includes': includes
    },

}

setup(
    name = "noaaaaaaaaa",
    options = options,
    version = "1.2",
    description = '<any description>',
    executables = executables
)
