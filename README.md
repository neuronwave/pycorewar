# PyCorewar

PyCorewar is a fast MARS with an easy to use Python interface. It is
released under The GNU General Public License, Version 2 (see the file
[COPYING](COPYING) for details).

At the moment the following features are supported:

- ICWS '88 (with multiwarrior support)
- ICWS '94 draft (without P-Space)
- most features of pMARS' parser

## Requirements

You need Python 3.6 or newer and a recent version of GCC for compiling PyCorewar.

## How to build and install

### Using pip (recommended)

Install from the current directory:

```bash
# Install in user directory (no admin privileges required)
pip install --user .

# Or, for development mode (changes to source immediately available)
pip install --user -e .
```

### Using a virtual environment (recommended for development)

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# When done, deactivate the virtual environment
deactivate
```

### Legacy method (not recommended)

```bash
python3 setup.py build
python3 setup.py install
```

## Bug reports

Please send any bug reports to [jens@gutzeit.name](mailto:jens@gutzeit.name).

## Note on Python Packaging

This package uses modern Python packaging with `pyproject.toml`. If you encounter any packaging issues, make sure you have the latest version of pip and setuptools:

```bash
pip install --upgrade pip setuptools wheel
```

## Thanks

Writing PyCorewar would have been almost impossible without the help of the
Core War Community:

- Sascha Zapf for endlessly running benchmarks and testsuites and providing
  lots of ideas.
- Albert Ma, Nandor Sieben, Stefan Strack and Mintardjo Wangsaw for writing
  pMARS
- M Joonas Pihlaja for writing exhaust, which made it very easy to understand
  the inner workings of a MARS
- Martin Ankerl for writing exhaust-ma, where I have found a lot of ideas
  for optimizing PyCorewar.
- Michal Janeczek for writing fmars, where I have found even more ideas for
  optimizing PyCorewar.
- Paul V-Khoung for several nice chats about optimizing PyCorewar
