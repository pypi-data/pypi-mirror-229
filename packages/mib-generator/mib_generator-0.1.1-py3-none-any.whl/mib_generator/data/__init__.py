"""The files and submodules in this package/folder serve as a storage of data and global-level
variables which are mostly stored here in order not to cluster the code somewhere else and in order
to be easily accessible by any other file.

The files/submodules here are:

    * :obj:`longdata` - This giant module stores mostly all information about the structures of MIB
      tables and what checks should be performed by each entry in them.
    * ``paths.json5`` - This file stores information about paths to the input/output files in a json5 format.
    * ``config.json5`` - This file stores config information which mostly include what pre-processor macros
      should be taken as defined when parsing the inputted files.
"""
