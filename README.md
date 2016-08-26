# bubble-tools
python routines related to bubble format

## validation
usage:

    python3 bubble-tool.py --validate path/to/bubble/file

Try hard to find errors and inconsistancies in the given bubble file

Spot powernode overlapping, inclusions inconsistancies and empty powernodes.
Profiling gives general informations about the file data.

## conversion to dot
usage:

    python3 bubble-tool.py --dot path/to/bubble/file path/to/output/file

Convert given bubble file in dot format.
