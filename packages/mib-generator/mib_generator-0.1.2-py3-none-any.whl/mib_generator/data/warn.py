"""Takes care of warning and errors that can be raised by the rest of the program.

This module holds both definition of all the errors and warnings that can occur throughout and a method that can be used to 
raise them. (This is made this centralised so that the raising method can be easily changed later if e.g. the UI changes.)

Attributes:
    warnings (dict): A dictionary containing the text definitions of all the possible warnings.
    errors (dict): A dictionary containing the text definitions of all the possible errors.
"""

warnings = {
    "WCC1": "Wasn't able to find matching calibration for {} in packet {}.",
    "WCC2": "Wasn't able to find matching decalibration for {} in command {}.",
    "WCC3": "Wasn't able to find the required verification {} for command {}.",
    "WCT1": "Wasn't able to find the common Tc header.",
    "WCT2": "Wasn't able to find the common Tm header.",
    "WCM1": "Wasn't able to find the numerical value of {}.",
    "WCM2": "Wasn't able to establish the link of packet {} to any header structure.",
    "WGM1": "Found repedition in table {}. Deleting rows: {}{}",
    "WGM2": "Tm-packets {} and {} share packet type, subtype and apid, but differ in specification of additional identification field.",
    "WGM3": "Tm-packets {} and {} share packet type, subtype and apid, but do not have additional identification field specified.",
    "WGM4": "The value in table {}, column {}, row {} doesn't have the required type.{}",
    "WGM5": "Missing a mandatory entry in table {}, column {}, row {}.",
    "WGG1": "Didn't get an input object on basis of which the table {} could be constructed.",
    "WGG2": "The construction of the table {} isn't yet implemented. And hence it wasn't generated.",
    "WMM1": "PySide6 not found. Please install it in order to show the parsed files",
    "WPL1": "Failed to construct the list of available enumerations.",
    "WPM1": "Invalid logic encountered when parsing preprocessor directives.",
}

errors = {
    "EPL1": "Failed to locate one of the C files.",
    "EPL2": "Failed to load one of the C files.",
    "EPM1": "Falied loading json5 comment: {}",
}


def raises(ID, *data):
    """Raise warning/error with the given ID.

    This method looks up a warning/error text for a given passed ID, formats it with other passed parameters and
    then displays it (for now printing it into console).

    Args:
        ID (str): The ID identifying the warning/error of format 3 capital letters + one-digit number.
        \*data (\*args): Additional parameters which are to be formatted into the warning/error text.
    """
    if ID[:1] in {"w", "W"}:
        if ID in warnings.keys():
            stri = "Warn.:\t" + warnings[ID].format(*data)
        else:
            stri = "Warn.:\tUnspecified warning with ID {} encountered.".format(ID)
    else:
        if ID in errors.keys():
            stri = "Error:\t" + errors[ID].format(*data)
        else:
            stri = "Error:\tUnspecified error with ID {} encountered.".format(ID)
    print(stri)
