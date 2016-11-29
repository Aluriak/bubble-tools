"""Bubble format related tools

usage:
    bubble-tool.py validate <bblfile> [--profiling]
    bubble-tool.py dot <bblfile> [<dotfile>] [--render]
    bubble-tool.py gexf <bblfile> [<gexffile>]

"""


import docopt

from bubbletools import validator
from bubbletools import converter
from bubbletools import utils


if __name__ == "__main__":
    args = docopt.docopt(__doc__)

    if args['validate']:
        logs = validator.validate(args['<bblfile>'],
                                  profiling=args['--profiling'])
        for log in logs:
            print(log)

    if args['dot']:
        print('Output file:', converter.bubble_to_dot(
            args['<bblfile>'],
            args['<dotfile>'],
            render=args['--render']
        ))

    if args['gexf']:
        print('Output file:', converter.bubble_to_gexf(
            args['<bblfile>'],
            args['<gexffile>'],
        ))
