"""Bubble format related tools

usage:
    bubble-tool.py validate <bblfile> [--profiling]
    bubble-tool.py dot <bblfile> [<dotfile>] [--render] [--oriented]
    bubble-tool.py gexf <bblfile> [<gexffile>] [--oriented]
    bubble-tool.py js <bblfile> <directory> [--oriented] [--run]

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
            render=args['--render'],
            oriented=args['--oriented']
        ))

    if args['gexf']:
        print('Output file:', converter.bubble_to_gexf(
            args['<bblfile>'],
            args['<gexffile>'],
            oriented=args['--oriented']
        ))

    if args['js']:
        print('Output file:', converter.bubble_to_js(
            args['<bblfile>'],
            jsdir=args['<directory>'],
            oriented=args['--oriented']
        ))
        if args['--run']:
            import webbrowser
            webbrowser.open(args['<directory>'] + '/index.html')
