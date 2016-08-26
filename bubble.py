"""Bubble format related tools

usage:
    bubble-tool.py --validate <bblfile> [--profiling]
    bubble-tool.py --dot <bblfile> [<dotfile>]

"""


import validator
import converter
import utils

import docopt



if __name__ == "__main__":
    args = docopt.docopt(__doc__)

    if args['--validate']:
        logs = validator.validate(utils.file_lines(args['<bblfile>']),
                                  profiling=args['--profiling'])
        for log in logs:
            print(log)

    if args['--dot']:
        lines = utils.file_lines(args['<bblfile>']),
        converter.to_dot(lines, args['<dotfile>'])
