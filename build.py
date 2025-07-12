#!/usr/bin/env python3
#
# Custom build script for PyCorewar
# This allows compiling the C extensions without using setuptools
#
# Usage: python build.py [--use-env]
#
# The --use-env flag will check for environment variables:
#   - PYCOREWAR_CFLAGS: Additional compiler flags
#   - PYCOREWAR_LDFLAGS: Additional linker flags
#   - PYCOREWAR_OUTPUT_DIR: Custom output directory (default: Corewar)

import os
import platform
import subprocess
import sys
import sysconfig
from pathlib import Path
import argparse

# Check Python version
if sys.version_info < (3, 6):
    raise RuntimeError("PyCorewar requires at least Python 3.6 to build.")

# C extension compilation arguments
EXTRA_COMPILE_ARGS = ["-O3", "-funroll-all-loops", "-std=c99"]

def parse_args():
    parser = argparse.ArgumentParser(description="Build PyCorewar C extensions")
    parser.add_argument("--use-env", action="store_true",
                        help="Use environment variables for build configuration")
    parser.add_argument("--output-dir", default="Corewar",
                        help="Output directory for compiled modules")
    parser.add_argument("--verbose", action="store_true",
                        help="Print detailed information during build")
    return parser.parse_args()

def run_build(args):
    """
    Run the manual build process
    """
    print("Building PyCorewar C extensions...")

    # Determine the directories
    src_dir = Path('src')
    output_dir = Path(args.output_dir)

    if args.use_env:
        output_dir = Path(os.environ.get('PYCOREWAR_OUTPUT_DIR', output_dir))

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Determine Python include paths and extension suffix
    python_include = sysconfig.get_path('include')
    python_platinclude = sysconfig.get_config_var('PLATINCLUDE') or ''
    extension_suffix = sysconfig.get_config_var('EXT_SUFFIX')

    # Platform-specific settings
    if platform.system() == 'Darwin':  # macOS
        ldflags = ["-undefined", "dynamic_lookup"]
        warning_flags = ["-Wno-nullability-completeness", "-Wno-ignored-optimization-argument"]
    else:  # Linux/other
        ldflags = []
        warning_flags = []

    # Use environment variables if requested
    if args.use_env:
        env_cflags = os.environ.get('PYCOREWAR_CFLAGS', '')
        if env_cflags:
            env_cflags = env_cflags.split()
        else:
            env_cflags = []

        env_ldflags = os.environ.get('PYCOREWAR_LDFLAGS', '')
        if env_ldflags:
            env_ldflags = env_ldflags.split()
        else:
            env_ldflags = []

        EXTRA_COMPILE_ARGS.extend(env_cflags)
        ldflags.extend(env_ldflags)

    # Base compiler flags
    cflags = EXTRA_COMPILE_ARGS + [
        f"-I{python_include}",
        f"-I{src_dir}",
        "-fPIC"
    ] + warning_flags

    # Add platform-specific include directory if it exists and is different
    if python_platinclude and python_platinclude != python_include:
        cflags.append(f"-I{python_platinclude}")

    if args.verbose:
        print(f"Python include path: {python_include}")
        print(f"Python platform include path: {python_platinclude}")
        print(f"Extension suffix: {extension_suffix}")
        print(f"Compiler flags: {cflags}")
        print(f"Linker flags: {ldflags}")
        print(f"Output directory: {output_dir}")

    # Compile the modules
    compile_module(
        "Redcode",
        [src_dir / "Redcodemodule.c"],
        output_dir,
        extension_suffix,
        cflags,
        ldflags,
        args.verbose
    )

    compile_module(
        "Benchmarking",
        [
            src_dir / "BenchWarrior.c",
            src_dir / "BenchPositioning.c",
            src_dir / "BenchMARS88.c",
            src_dir / "BenchMARS94nop.c",
            src_dir / "Benchmarkingmodule.c"
        ],
        output_dir,
        extension_suffix,
        cflags,
        ldflags,
        args.verbose
    )

    compile_module(
        "Optimizing",
        [
            src_dir / "BenchWarrior.c",
            src_dir / "BenchPositioning.c",
            src_dir / "OptMARS94nop.c",
            src_dir / "Optimizingmodule.c"
        ],
        output_dir,
        extension_suffix,
        cflags,
        ldflags,
        args.verbose
    )

    # Create or update __init__.py
    init_path = output_dir / "__init__.py"
    if not init_path.exists():
        with open(init_path, 'w') as f:
            f.write("# PyCorewar package\n")

    print(f"Compilation complete. Extension modules are in {output_dir}/")
    print("To use these modules, you can import them with: 'from Corewar import Redcode, Benchmarking, Optimizing'")

def compile_module(name, source_files, output_dir, extension_suffix, cflags, ldflags, verbose=False):
    """
    Compile a single module with the given source files
    """
    print(f"Compiling {name} module...")

    output_file = output_dir / f"{name}{extension_suffix}"

    # Construct the command
    cmd = ["gcc"] + cflags + ["-shared"] + ldflags + ["-o", str(output_file)] + [str(f) for f in source_files]

    if verbose:
        print(f"Running command: {' '.join(cmd)}")

    # Run the compilation
    try:
        result = subprocess.run(cmd, check=True, capture_output=not verbose)
    except subprocess.CalledProcessError as e:
        print(f"Failed to compile {name} module")
        if not verbose:
            print(e.stderr.decode())
        sys.exit(e.returncode)

    print(f"Successfully compiled {name} module")

if __name__ == "__main__":
    args = parse_args()
    run_build(args)
