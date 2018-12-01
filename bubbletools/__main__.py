"""Bubble format related tools

usage:
    bubble-tool.py validate <bblfile> [--profiling]
    bubble-tool.py dot <bblfile> [<dotfile>] [--render] [--oriented]
    bubble-tool.py gexf <bblfile> [<gexffile>] [--oriented]
    bubble-tool.py js <bblfile> <directory> [--oriented] [--render] [<style>...]

"""


import ast
import docopt

from bubbletools import validator
from bubbletools import converter
from bubbletools import utils


def read_style_args(args:dict) -> dict:
    def make_value(val):
        try:
            return ast.literal_eval(val)
        except SyntaxError:
            return str(val)
    style_args = (arg.split('=') for arg in args)
    style_args = {arg: make_value(val) for arg, val in style_args}
    return style_args


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
        style_args = read_style_args(args['<style>'])
        print('Output file:', converter.bubble_to_js(
            args['<bblfile>'],
            jsdir=args['<directory>'],
            oriented=args['--oriented'],
            **style_args
        ))
        if args['--render']:
            import os
            import webbrowser
            single_js_file = os.path.splitext(args['<directory>'])[1] == '.html'
            uri = os.path.join(os.getcwd(), args['<directory>']
                               + ('' if single_js_file else '/index.html'))
            print(f'OPENING "{uri}" in browser…')
            webbrowser.open(uri)
