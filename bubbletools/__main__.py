"""Bubble format related tools

usage:
    bubble-tool.py validate <bblfile> [--profiling]
    bubble-tool.py dot <bblfile> [<dotfile>] [--render]

"""


import docopt

from bubbletools import validator
from bubbletools import converter
from bubbletools import utils


if __name__ == "__main__":
    args = docopt.docopt(__doc__)

    if args['validate']:
        logs = validator.validate(utils.file_lines(args['<bblfile>']),
                                  profiling=args['--profiling'])
        for log in logs:
            print(log)

    if args['dot']:
        print('Output file:', converter.bubble_to_dot(
            args['<bblfile>'],
            args['<dotfile>'],
            render=args['--render']
        ))
