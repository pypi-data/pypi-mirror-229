"""This module holds method/s which take care of transferring the correct config files into the runtime directory.
"""
import os
import shutil


def move_conf(dire=None):
    """Transfer the config files from the specified directory to runtime location.

    This method looks at the passed directory, checks what config files are inside it and if such are found, moves them
    to the package runtime directory (:obj:`mib_generator.temp`), rewriting config files which might have been there already.
    If some config file is not found in the specified directory, transfers config from the default directory
    (:obj:`mib_generator.data`) instead.

    Args:
        dire (str): A string specifying the directory from which the config files are to be taken.
    """
    here = os.path.dirname(__file__)
    data = os.path.join(os.path.dirname(here), "data")
    if dire and os.path.isfile(os.path.join(dire, "paths.json5")):
        source_p = os.path.join(dire, "paths.json5")
    else:
        source_p = os.path.join(data, "paths.json5")
    shutil.copy(source_p, here)
    if dire and os.path.isfile(os.path.join(dire, "config.json5")):
        source_c = os.path.join(dire, "config.json5")
    else:
        source_c = os.path.join(data, "config.json5")
    shutil.copy(source_c, here)
