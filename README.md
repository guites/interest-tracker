# interest-tracker

Study mapping and tracker

## Installation

There are no dependencies aside from Python 3.10+.

1. Clone the repository and change into the directory.
2. Add executable permission to the script: `chmod u+x interest_tracker.py`.

## Development

1. Create a virtual environment and activate it.

    python3 -m venv .venv
    source .venv/bin/activate
2. Install dependencies from `dev_requirements.txt`: `pip3 install -r dev_requirements.txt`.
3. Run tests with `python3 -m pytest`.

## Usage

Basic interest creation:

```
./interest-tracker.py log "OOP using default python classes and object" --effort 00:15 --tags python,oop
```

You can use shorthand syntax on the `effort` and `tags` flags:

```
./interest-tracker.py log "study usage of subcommands with python argparser" -e 00:15 -t python,cli
```

You can prompt the script for help using

    # help for specific commands
    ./interest-tracker.py visualize -h
    ./interest-tracker.py log -h
    # or general program wide help
    ./interest-tracker.py -h

Visualize existing interests:

```
./interest-tracker.py visualize
```

## References

1. [argparse](https://docs.python.org/3/howto/argparse.html)
2. [python's sqlite3 lib](https://docs.python.org/3/library/sqlite3.html)
3. For parsing arbitrary time intervals (3h, 32m, 07h30, 07:30, etc) we could use [pytimeparse](https://github.com/wroberts/pytimeparse) or maybe [parsedatetime](https://github.com/bear/parsedatetime)
4. [subcommands with argparse](https://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html)
