#!/usr/bin/env python3
#
# Test script to verify that the C extensions are working properly
#

import sys
import os

# Add the parent directory to the path to ensure we can import corewar
# Ensure the parent directory is in the path to allow importing the corewar package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the modules directly
    from Corewar import Redcode, Benchmarking, Optimizing
    print("Successfully imported all corewar modules:")
    print(f" - Redcode: {Redcode}")
    print(f" - Benchmarking: {Benchmarking}")
    print(f" - Optimizing: {Optimizing}")
    print("\nImport successful!")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Test creating a basic Redcode parser
try:
    parser = Redcode.Parser()
    print("\nCreated Redcode parser successfully")
    print(f"Parser object: {parser}")
except Exception as e:
    print(f"Error creating parser: {e}")
    sys.exit(1)

print("\nAll tests passed!")
