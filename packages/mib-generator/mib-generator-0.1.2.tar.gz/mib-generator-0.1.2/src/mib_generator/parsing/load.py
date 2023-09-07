"""Central location from which other modules can source data from the parsed C-files.

This module is initialised in the first step of the MIB construction process. At its initialisation the C-files
are loaded from the defined paths, are parsed using the :obj:`mib_generator.parsing.parser_main.main` method and are
subsequently available for other scripts throughout the rest of the MIB construction process. The only other
method here is :obj:`extr_values` which serves the purpose creating a global evaluation dictionary holding
values from all header enums, macros, etc...

Attributes:
    TmH (parsing.parser_main.file): Holds the Python parsed representation of the Tm-header C-file.
    TcH (parsing.parser_main.file): Holds the Python parsed representation of the Tc-header C-file.
    TcTmH (parsing.parser_main.file): Holds the Python parsed representation of the TcTm-header C-file.
    TmC (parsing.parser_main.file): Holds the Python parsed representation of the Tm (normal) C-file.
    enumerations (dict): A dictionary containing all possible usable evaluations/enumerations sourced 
        form enums, macros, etc... found in all 3 of the parsed header files.
"""
import os

import json5

import mib_generator.data.warn as warn
import mib_generator.parsing.parser_main as par

try:
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "temp", "paths.json5"
    )
    file = open(file_path, "r")
    paths = json5.load(file)
    file.close()

    TmC_path = paths["TmFile"]
    TmH_path = paths["TmHeader"]
    TcH_path = paths["TcHeader"]
    TcTmH_path = paths["TcTmHeader"]
    out_dir = paths["OutDir"]
    out_doc = paths["OutDoc"]
except:
    warn.raises("EPL1")
    TmC_path = ""
    TmH_path = ""
    TcH_path = ""
    TcTmH_path = ""
    out_dir = ""
    out_doc = ""

try:
    TmH = par.main(TmH_path)
    TcH = par.main(TcH_path)
    TcTmH = par.main(TcTmH_path)
    TmC = par.main(TmC_path)
except:
    warn.raises("EPL2")
    TmH = None
    TcH = None
    TcTmH = None
    TmC = None


def extr_values(file):
    """Create a dictionary from constants, ``enum`` correspondences, etc... in the given file.

    Goes through all objects in the parsed file and for each ``enum`` and macro, appends the name-value
    pairs present to a dictionary (which represents the "global" evaluation in the file).

    Args:
        file (parsing.parser_main.file): File from which the evaluation dictionary is to be extracted.

    Returns:
        dict: A dictionary with all possible "global" evaluation found in the given file.
    """
    lis = {}
    for x in file.structures:
        if x.type == "enum":
            lis.update(x.entries)
        if x.type == "define":
            name = x.name
            if "(" in x.expression:
                value_raw = x.expression[1:-1]
            else:
                value_raw = x.expression
            try:
                value = int(value_raw)
            except:
                value = None
            if value is not None:
                lis[name] = value
    return lis


try:
    enum1 = extr_values(TmH)
    enum2 = extr_values(TcTmH)
    enum3 = extr_values(TcH)
    enumerations = enum1 | enum2 | enum3
except:
    warn.raises("WPL1")
    enumerations = {}
