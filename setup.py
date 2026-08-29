import os
from pathlib import Path
import shutil
import subprocess
import sys

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import versioneer


# A CMakeExtension needs a sourcedir instead of a file list.
# The name must be the _single_ output extension from the CMake build.
# If you need multiple extensions, see scikit-build.
class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def build_extension(self, ext):
        if self.compiler.compiler_type == "msvc":
            raise NotImplementedError("pymgl is not supported on Windows")

        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        # required for auto-detection of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        cfg = "Debug" if self.debug else "Release"
        print(f"Build mode: {cfg}")

        cmake_args = [
            f"-DCMAKE_PYTHON_PATH={Path(sys.executable).parent.parent}",
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DVERSION_INFO={self.distribution.get_version()}",
            f"-DCMAKE_BUILD_TYPE={cfg}",
        ]

        if shutil.which('ccache'):
            cmake_args.append("-DCMAKE_CXX_COMPILER_LAUNCHER=ccache")

        build_args = []

        cmake_generator = os.environ.get("CMAKE_GENERATOR", "")
        if not cmake_generator:
            cmake_args += ["-GNinja"]

        # Set CMAKE_BUILD_PARALLEL_LEVEL to control the parallel build level
        # across all generators.
        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            # self.parallel is a Python 3 only way to set parallel jobs by hand
            # using -j in the build_ext call, not supported by pip or PyPA-build.
            if hasattr(self, "parallel") and self.parallel:
                build_args += ["-j{}".format(self.parallel)]

        tmp_dir = os.environ.get("BUILD_TEMP_DIR", self.build_temp)

        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        subprocess.check_call(["cmake", ext.sourcedir] + cmake_args, cwd=tmp_dir)
        subprocess.check_call(["cmake", "--build", "."] + build_args, cwd=tmp_dir)


release_version = os.environ.get("PYMGL_RELEASE_VERSION")
cmdclass = versioneer.get_cmdclass()

if release_version:
    versioneer_build_py = cmdclass["build_py"]

    class ReleaseBuildPy(versioneer_build_py):
        """Write the pre-tag release version into the packaged runtime."""

        def run(self):
            super().run()
            version_file = Path(self.build_lib) / "pymgl" / "_version.py"
            version_file.write_text(
                "# Generated for a pre-tag release build.\n"
                f"__version__ = {release_version!r}\n"
                "def get_versions():\n"
                "    return {\"version\": __version__, \"full-revisionid\": \"\", "
                "\"dirty\": False, \"error\": None, \"date\": None}\n",
                encoding="utf-8",
            )

    cmdclass["build_py"] = ReleaseBuildPy

cmdclass.update({"build_ext": CMakeBuild})

setup(
    # Allows exact release artifacts to be prepared before the corresponding
    # signed tag is created. Normal development and tagged builds still use
    # Versioneer's Git-derived version.
    version=release_version or versioneer.get_version(),
    include_package_data=True,
    exclude_package_data={"": ["*.h", "*.c"]},
    cmdclass=cmdclass,
    ext_modules=[CMakeExtension("pymgl._pymgl")],
)
