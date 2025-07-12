#!/bin/bash
#
# Script to manually compile C extensions for the PyCorewar package without using setup.py
# Run from the pycorewar directory

set -e  # Exit on error

# Get Python include directory and extension suffix
PYTHON_INCLUDE=$(python3 -c "import sysconfig; print(sysconfig.get_path('include'))")
PYTHON_PLATINCLUDE=$(python3 -c "import sysconfig; print(sysconfig.get_config_var('PLATINCLUDE') or '')")
EXTENSION_SUFFIX=$(python3 -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))")
OUTPUT_DIR="Corewar"

# Ensure output directory exists
mkdir -p ${OUTPUT_DIR}

# Determine OS-specific settings
UNAME=$(uname)
if [ "$UNAME" = "Darwin" ]; then
    # macOS specific flags
    LDFLAGS="-undefined dynamic_lookup"
    # Suppress warnings that are common on macOS
    CFLAGS_WARNINGS="-Wno-nullability-completeness -Wno-ignored-optimization-argument"
else
    # Linux/other flags
    LDFLAGS=""
fi

# Compiler flags from setup.py
CFLAGS="-O3 -funroll-all-loops -std=c99 -I${PYTHON_INCLUDE} -Isrc ${CFLAGS_WARNINGS:-}"

# Add platform-specific include directory if it exists and is different from PYTHON_INCLUDE
if [ -n "$PYTHON_PLATINCLUDE" ] && [ "$PYTHON_PLATINCLUDE" != "$PYTHON_INCLUDE" ]; then
    CFLAGS="$CFLAGS -I${PYTHON_PLATINCLUDE}"
fi

# Add Python.h include path and shared library flags
CFLAGS="${CFLAGS} -fPIC"

echo "Compiling with flags: ${CFLAGS}"
echo "Extension suffix: ${EXTENSION_SUFFIX}"
echo "Output directory: ${OUTPUT_DIR}"

# 1. Compile Redcode module
echo "Compiling Redcode module..."
gcc ${CFLAGS} ${LDFLAGS} -shared -o ${OUTPUT_DIR}/Redcode${EXTENSION_SUFFIX} src/Redcodemodule.c || {
    echo "Failed to compile Redcode module"
    exit 1
}

# 2. Compile Benchmarking module
echo "Compiling Benchmarking module..."
gcc ${CFLAGS} ${LDFLAGS} -shared -o ${OUTPUT_DIR}/Benchmarking${EXTENSION_SUFFIX} \
    src/BenchWarrior.c \
    src/BenchPositioning.c \
    src/BenchMARS88.c \
    src/BenchMARS94nop.c \
    src/Benchmarkingmodule.c || {
    echo "Failed to compile Benchmarking module"
    exit 1
}

# 3. Compile Optimizing module
echo "Compiling Optimizing module..."
gcc ${CFLAGS} ${LDFLAGS} -shared -o ${OUTPUT_DIR}/Optimizing${EXTENSION_SUFFIX} \
    src/BenchWarrior.c \
    src/BenchPositioning.c \
    src/OptMARS94nop.c \
    src/Optimizingmodule.c || {
    echo "Failed to compile Optimizing module"
    exit 1
}

echo "Compilation complete. Extension modules are in ${OUTPUT_DIR}/"
echo "To use these modules, you can import them with: 'from Corewar import Redcode, Benchmarking, Optimizing'"
