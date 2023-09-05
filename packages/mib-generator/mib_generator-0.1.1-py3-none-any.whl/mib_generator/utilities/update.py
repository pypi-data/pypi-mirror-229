"""Various CLI scripts that update various files that configure the generation process.

This module holds methods that allow the user to easily modify various files that affects the behaviour of the main Python
script. They can be called by simply importing and calling them or through appropriate flags build into the main CLI of the 
MIB generator.  
"""
import json5
import os


def update_path():
    """Run a series of queries asking user to specify valid paths to input files.

    This method allows the user to specify paths to the 4 input files and 1 output directory that the MIB generator requires.
    The previously stored values are shown to the user and he can leave them be or choose to modify them stating the location of
    the target files either in terms of absolute or relative path. The inputted location is then checked and if it exists, then
    the path is saved (in absolute form). Only existence is checked, not that the file is valid for the given purpose.
    """
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "paths.json5"
    )
    fil = open(file_path, "r")
    leg_data = json5.load(fil)
    fil.close()
    data = {}
    valid_TmH = False
    print("The current absolute path is: " + os.getcwd())
    print("------")
    while not valid_TmH:
        print("State relative or absolute path to Tm Header file.")
        print("Currently this path is: " + str(leg_data["TmHeader"]))
        print("(press Enter if you want to keep this value)")
        path = input("Path: ")
        if path == "" and os.path.isfile(leg_data["TmHeader"]):
            data["TmHeader"] = leg_data["TmHeader"]
            valid_TmH = True
        elif os.path.isfile(path):
            data["TmHeader"] = os.path.abspath(path)
            valid_TmH = True
        else:
            print("Error:\tFailed to find the specified file, try again.")
        print("------")
    valid_TcTmH = False
    while not valid_TcTmH:
        print("State relative or absolute path to TcTm Header file.")
        print("Currently this path is: " + str(leg_data["TcTmHeader"]))
        print("(press Enter if you want to keep this value)")
        path = input("Path: ")
        if path == "" and os.path.isfile(leg_data["TcTmHeader"]):
            data["TcTmHeader"] = leg_data["TcTmHeader"]
            valid_TcTmH = True
        elif os.path.isfile(path):
            data["TcTmHeader"] = os.path.abspath(path)
            valid_TcTmH = True
        else:
            print("Error:\tFailed to find the specified file, try again.")
        print("------")
    valid_TmC = False
    while not valid_TmC:
        print("State relative or absolute path to Tm C file.")
        print("Currently this path is: " + str(leg_data["TmFile"]))
        print("(press Enter if you want to keep this value)")
        path = input("Path: ")
        if path == "" and os.path.isfile(leg_data["TmFile"]):
            data["TmFile"] = leg_data["TmFile"]
            valid_TmC = True
        elif os.path.isfile(path):
            data["TmFile"] = os.path.abspath(path)
            valid_TmC = True
        else:
            print("Error:\tFailed to find the specified file, try again.")
        print("------")
    valid_TcH = False
    while not valid_TcH:
        print("State relative or absolute path to Tc Header file.")
        print("Currently this path is: " + str(leg_data["TcHeader"]))
        print("(press Enter if you want to keep this value)")
        path = input("Path: ")
        if path == "" and os.path.isfile(leg_data["TcHeader"]):
            data["TcHeader"] = leg_data["TcHeader"]
            valid_TcH = True
        elif os.path.isfile(path):
            data["TcHeader"] = os.path.abspath(path)
            valid_TcH = True
        else:
            print("Error:\tFailed to find the specified file, try again.")
        print("------")
    valid_Out = False
    while not valid_Out:
        print("State relative or absolute path to the output directory.")
        print("Currently this path is: " + str(leg_data["OutDir"]))
        print("(press Enter if you want to keep this value)")
        path = input("Path: ")
        if path == "" and os.path.isdir(leg_data["OutDir"]):
            data["OutDir"] = leg_data["OutDir"]
            valid_Out = True
        elif os.path.isdir(path):
            data["OutDir"] = os.path.abspath(path)
            valid_Out = True
        else:
            print("Error:\tFailed to find the specified directory, try again.")
        print("------")
    fil = open(file_path, "w")
    fil.write("// This file stores various paths to source/output files\n")
    fil.write(json5.dumps(data))
    fil.close()


def update_config():
    """Run a series of queries asking user to specify configuration parameters.

    This method allows the user to specify various configuration parameters. First, the already saved parameters are loaded
    and the user is asked whether he wants to keep the current value, change it or delete the parameter altogether. Then,
    the user is given the option to create a new parameter. The only valid accepted of parameters are boolean or a string.
    """
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "config.json5"
    )
    fil = open(file_path, "r")
    leg_data = json5.load(fil)
    fil.close()
    data = {}
    print("To change the config parameters:")
    print('Write "True" to set the parameter to True.')
    print('Write "False" to set the parameter to False.')
    print('Write "DEL" to delete this parameter.')
    print("Write anything else to store that value as a string.")
    print("Leave the input field blank to leave the value unchanged.")
    print("------")
    for i in leg_data:
        print(
            "Set value of parameter "
            + i
            + ", which is currently set to "
            + str(leg_data[i])
            + "."
        )
        x = input("Input: ")
        if x == "True":
            data[i] = True
        elif x == "False":
            data[i] = False
        elif x == "DEL":
            pass
        elif x == "":
            data[i] = leg_data[i]
        else:
            data[i] = x
        print("------")
    additional = True
    while additional:
        print(
            "If you want to add additional parameter, input parameter name (otherwise leave the field blank)."
        )
        y = input("Input: ")
        if not y:
            additional = False
        else:
            print("Set value of this parameter " + y + " (as above).")
            x = input("Input: ")
            if x == "True":
                data[y] = True
            elif x == "False":
                data[y] = False
            elif x == "DEL":
                pass
            elif x == "":
                data[y] = ""
            else:
                data[y] = x
            print("------")
    fil = open(file_path, "w")
    fil.write("// This file stores various definitions used mainly by the parser\n")
    fil.write(json5.dumps(data))
    fil.close()
