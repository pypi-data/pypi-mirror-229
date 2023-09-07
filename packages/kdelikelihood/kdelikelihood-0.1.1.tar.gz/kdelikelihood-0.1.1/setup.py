"""
@author: Samuel M. Fischer
"""
from os import path
import os
import re
import subprocess

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext as _build_ext


# ==== Basic settings ====

# Name of the extension
NAME = "_kde_tools"

# Change this to `True` if you want to profile the code
profile = False

# Name of the package (and directory of pyx and pxd files)
packageName = "kdelikelihood"

currentFolder = path.dirname(path.abspath(__file__))

# Read the long description
with open(path.join(currentFolder, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

package_dir = path.join(currentFolder, "src", packageName)

# Change some options, if we want to profile the code
if profile:
    print("Compiling with profiling option switched on!")
    define_macros = [("CYTHON_TRACE", "1")]
    compiler_directives = {"linetrace": True, "binding": True}
    from Cython.Compiler.Options import get_directive_defaults

    directive_defaults = get_directive_defaults()
    directive_defaults["linetrace"] = True
    directive_defaults["binding"] = True
else:
    define_macros = []
    # compiler_directives={'boundscheck':False, 'wraparound':False, "nonecheck":False}
    compiler_directives = {}


def find_vcvarsall():
    # look if vcvarsall is already on the PATH
    try:
        subprocess.call("vcvasall.bat")
        return "vcvasall.bat"
    except FileNotFoundError:
        pass

    results = []
    for programFilesDir in os.environ["PROGRAMFILES"], os.environ["PROGRAMFILES(X86)"]:
        for visualStudioDir in os.scandir(programFilesDir):
            if "Visual Studio" not in visualStudioDir.name:
                continue
            for yearVersionDir in os.scandir(visualStudioDir):
                if not yearVersionDir.name.isnumeric:
                    continue
                for versionDir in os.scandir(yearVersionDir):
                    pathCandidate = path.join(versionDir.path, "VC/Auxiliary/Build/vcvarsall.bat")
                    if path.exists(pathCandidate):
                        results.append(pathCandidate)

    # return the newest version of vcvarsall
    if results:
        return path.normpath(results[-1])

    print(
        "The Visual Studio Compiler file 'vcvarsall.bat' was not found at the place where it was expected.\n"
        "You may find help at https://docs.microsoft.com/de-de/cpp/build/building-on-the-command-line\n"
        "If you do not have Visual Studio installed, please abort with [Ctrl]-[C] and install it."
    )
    while True:
        pathCandidate = input(
            "Please provide the full path to 'vcvarsall.bat' and press [Enter].\n>>> "
        )
        if not pathCandidate.endswith("vcvarsall.bat"):
            pathCandidate = path.join(pathCandidate, "vcvarsall.bat")
        if path.exists(pathCandidate):
            return path.normpath(pathCandidate)
        print(
            "vcvarsall.bat could not be found at the place you specified. "
            "Please try again or press [Ctrl]-[C] to abort."
        )


def remove_dependency_of_python_debug_version(cppExtension):
    # Read in the file
    with open(cppExtension, "r") as file:
        filedata = file.read()

    # Check whether the file has been processed already by searching
    # for a signature string that would occur after processing
    # and is unlikely to be included in unprocesses files
    searchStr = "#undef _DEBUG\s*#include <Python.h>\s*#define _DEBUG"
    if re.search(searchStr, filedata) is not None:
        return

    # Replace the target string
    replaceStr = """
    
        // This section has been manually introduced to avoid dependency
        // on a debug version of python and to fix an issue with VS2022
        // See https://github.com/microsoft/onnxruntime/issues/9735#issuecomment-970718821
        
        #if defined(_MSC_VER)
        #    if (PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION < 4)
        #        define HAVE_ROUND 1
        #    endif
        #    include <corecrt.h>
        #    pragma warning(push)
        #    pragma warning(disable : 4510 4610 4512 4005)
        #endif
        
        #ifdef _DEBUG
          #undef _DEBUG
          #include <Python.h> 
          #define _DEBUG
        #else
          #include <Python.h>
        #endif
        // --------------------------------------------------------------
        
        """
    #    if defined(_DEBUG) && !defined(Py_DEBUG)
    #        define PYBIND11_DEBUG_MARKER
    #        undef _DEBUG
    #    endif
    filedata = re.sub('\s#include "Python.h"\s', replaceStr, filedata)

    # Write the file out again
    with open(cppExtension, "w") as file:
        file.write(filedata)


def insert_vcvars_path(arguments, vcvarsallString="vcvarsall.bat", vcvarsallPath=None):
    for i, item in enumerate(arguments):
        if vcvarsallString in item:
            if vcvarsallPath is None:
                vcvarsallPath = find_vcvarsall()
            arguments[i] = item.replace(vcvarsallString, vcvarsallPath)

    return arguments


# ==== Create a new factory function to import external dependencies AFTER they have been installed ====


class build_ext(_build_ext):
    def finalize_options(self):
        # Call the original function
        _build_ext.finalize_options(self)

        # Import numpy
        # Prevent numpy from thinking it is still in its setup process:
        # __builtins__.__NUMPY_SETUP__ = False
        import numpy

        self.include_dirs.append(numpy.get_include())

        # Cythonize
        from Cython.Build import cythonize

        self.distribution.ext_modules = cythonize(
            self.distribution.ext_modules,
            compiler_directives=compiler_directives,
            language_level="3",
            annotate=True,
            # force=True  # this is required if generated cpp files
            # shall not be reused. This increases
            # compatibility over python version but
            # takes additional time when building
        )


# ==== Collect the cpp source files and folders ====

# List the source directories
include_dirs = [package_dir]


# ==== prepare the Formind compilation ====


# ==== Create extension objects summarizing the information needed for the build ====

extensions = [
    Extension(
        packageName + "." + NAME,
        [path.join("src", packageName, NAME + ".pyx")],
        language="c++",
        include_dirs=include_dirs,
        define_macros=define_macros,  # needed for profiling
    )
]


if __name__ == "__main__":
    setup(
        cmdclass={"build_ext": build_ext},
        ext_modules=extensions,
        packages=[packageName],
        package_data={
            packageName: ["*.pxd", "*.pyx", "*.cpp", "*.c", "*.h"],
        },
    )
