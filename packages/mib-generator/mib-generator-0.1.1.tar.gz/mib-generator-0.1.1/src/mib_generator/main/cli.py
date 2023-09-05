"""Provides a simple CLI that can be accessed by the user.

If ran directly as a Python script, this module provides the user with a simple CLI which allows for specification of
various options for runtime of the script itself (whether the MIB databases should be constructed, whether saved, 
whether the parsed file should be visualised, etc..). It also provides a quick ``--help`` summary and an option to
run scripts for updating the config and paths files before running the generating script itself. 
"""

def cli_run():
    """Manages the CLI and runs the program.

    This is the main method that is run by external calls that want to run the whole program.
    It takes no arguments but assuming it is run as a bash/terminal program, it tries to parse and
    interpret passed flags and options and creates a small CLI interface which can be presented to the user
    with the ``--help`` flag.
    """
    import mib_generator.main.main as main
    import argparse
    
    prog = "MIB Creator"
    desc = "Creates MIB databases from C-files defined in paths.json5"
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument(
        "-v",
        "--visualise",
        help="show the contents of parsed files in GUI (requires PySide6 installed)",
        action="store_true",
    )
    parser.add_argument(
        "-x",
        "--xgenerate",
        help="run without generating MIB files",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--onlyparse",
        help="stop after parsing the C-files (does not also generate MIB files)",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--update_paths",
        help="start by running script to update paths and store them in the json5 file",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--update_config",
        help="start by running script to update config parameters (stored in json5 file)",
        action="store_true",
    )
    arguments = parser.parse_args()
    main.main(
        arguments.visualise,
        not arguments.xgenerate,
        arguments.onlyparse,
        arguments.update_paths,
        arguments.update_config,
    )


if __name__ == "__main__":
    import sys, os
    file_path = os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))
    )
    sys.path.append(file_path)
    cli_run()
