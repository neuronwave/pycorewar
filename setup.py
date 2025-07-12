#!/usr/bin/env python3
#
# Copyright (C) 2006 Jens Gutzeit <jens@jgutzeit.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Usage: pip install .

import os
import platform
import subprocess
import sys
from pathlib import Path
from setuptools import setup, Extension, Command
from setuptools.command.build_ext import build_ext

# Check Python version
if sys.version_info < (3, 6):
    raise RuntimeError("PyCorewar requires at least Python 3.6 to build.")

# C extension compilation arguments
EXTRA_COMPILE_ARGS = ["-O3", "-funroll-all-loops", "-std=c99"]

class CustomBuildExt(build_ext):
    """
    Custom build_ext command that can either use setuptools or manual compilation
    depending on environment variables

    This allows compiling the C extensions directly without relying on setuptools' build process.
    """

    def run(self):
        # Check if we should use the manual compilation method
        if os.environ.get('PYCOREWAR_MANUAL_BUILD', '').lower() in ('1', 'true', 'yes'):
            self.run_manual_build()
        else:
            # Otherwise, use the standard setuptools build
            build_ext.run(self)

    def run_manual_build(self):
        """
        Run a manual build process similar to the compile.sh script
        """
        print("Using manual build process for C extensions")

        # Determine the directories
        package_dir = Path(self.build_lib) / 'Corewar'
        src_dir = Path('src')

        # Ensure output directory exists
        os.makedirs(package_dir, exist_ok=True)

        # Copy the existing __init__.py if it exists in the source
        src_init = Path('Corewar') / '__init__.py'
        if src_init.exists():
            import shutil
            shutil.copy2(src_init, package_dir / '__init__.py')

        # Determine Python include paths and extension suffix
        python_include = Path(sys.executable).parent.parent / 'include' / f'python{sys.version_info.major}.{sys.version_info.minor}'
        if not python_include.exists():
            # Try sysconfig to get the include path
            import sysconfig
            python_include = sysconfig.get_path('include')
            python_platinclude = sysconfig.get_config_var('PLATINCLUDE') or ''
        else:
            python_platinclude = ''

        extension_suffix = self.get_ext_filename('')[1:]  # Remove the leading dot

        # Platform-specific settings
        if platform.system() == 'Darwin':  # macOS
            ldflags = ["-undefined", "dynamic_lookup"]
            warning_flags = ["-Wno-nullability-completeness", "-Wno-ignored-optimization-argument"]
        else:  # Linux/other
            ldflags = []
            warning_flags = []

        # Base compiler flags
        cflags = EXTRA_COMPILE_ARGS + [
            f"-I{python_include}",
            f"-I{src_dir}",
            "-fPIC"
        ] + warning_flags

        # Add platform-specific include directory if it exists and is different
        if python_platinclude and python_platinclude != str(python_include):
            cflags.append(f"-I{python_platinclude}")

        # Compile the modules
        self.compile_module(
            "Redcode",
            [src_dir / "Redcodemodule.c"],
            package_dir,
            extension_suffix,
            cflags,
            ldflags
        )

        self.compile_module(
            "Benchmarking",
            [
                src_dir / "BenchWarrior.c",
                src_dir / "BenchPositioning.c",
                src_dir / "BenchMARS88.c",
                src_dir / "BenchMARS94nop.c",
                src_dir / "Benchmarkingmodule.c"
            ],
            package_dir,
            extension_suffix,
            cflags,
            ldflags
        )

        self.compile_module(
            "Optimizing",
            [
                src_dir / "BenchWarrior.c",
                src_dir / "BenchPositioning.c",
                src_dir / "OptMARS94nop.c",
                src_dir / "Optimizingmodule.c"
            ],
            package_dir,
            extension_suffix,
            cflags,
            ldflags
        )

        # Ensure output directory exists
        os.makedirs(package_dir, exist_ok=True)

        # Create or update __init__.py
        init_path = package_dir / "__init__.py"
        if not init_path.exists():
            with open(init_path, 'w') as f:
                f.write("# PyCorewar package\n")

        print(f"Compilation complete. Extension modules are in {package_dir}/")

        # Make sure wheel directory exists for installation
        wheel_dir = Path(self.build_lib).parent / 'bdist.macosx-10.9-universal2' / 'wheel' / 'Corewar'
        os.makedirs(wheel_dir, exist_ok=True)

    def compile_module(self, name, source_files, output_dir, extension_suffix, cflags, ldflags):
        """
        Compile a single module with the given source files
        """
        print(f"Compiling {name} module...")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        output_file = output_dir / f"{name}{extension_suffix}"

        # Construct the command
        cmd = ["gcc"] + cflags + ["-shared"] + ldflags + ["-o", str(output_file)] + [str(f) for f in source_files]

        # Run the compilation
        result = subprocess.run(cmd, check=False)

        if result.returncode != 0:
            print(f"Failed to compile {name} module")
            sys.exit(result.returncode)


# Define the extension modules
ext_modules = [
    Extension(
        "Corewar.Redcode",
        include_dirs=["src/"],
        sources=["src/Redcodemodule.c"],
        extra_compile_args=EXTRA_COMPILE_ARGS,
    ),
    Extension(
        "Corewar.Benchmarking",
        include_dirs=["src/"],
        sources=[
            "src/BenchWarrior.c",
            "src/BenchPositioning.c",
            "src/BenchMARS88.c",
            "src/BenchMARS94nop.c",
            "src/Benchmarkingmodule.c",
        ],
        extra_compile_args=EXTRA_COMPILE_ARGS,
    ),
    Extension(
        "Corewar.Optimizing",
        include_dirs=["src/"],
        sources=[
            "src/BenchWarrior.c",
            "src/BenchPositioning.c",
            "src/OptMARS94nop.c",
            "src/Optimizingmodule.c",
        ],
        extra_compile_args=EXTRA_COMPILE_ARGS,
    ),
]

# Create empty directories that might be needed during installation
for directory in ['build/lib.macosx-10.9-universal2-cpython-310/Corewar',
                 'build/bdist.macosx-10.9-universal2/wheel/Corewar']:
    os.makedirs(directory, exist_ok=True)

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": CustomBuildExt},
    packages=["Corewar"],
    package_data={"Corewar": ["*.so"]},
)
