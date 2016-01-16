#!/usr/bin/env python3

import os
from argparse import ArgumentParser
from glob import glob

from aot import get_board_description
from aot.board import SvgBoardCreator


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Generate svg file for each board found in input.')
    parser.add_argument(
        '-i', '--input',
        help='directory of the json files describing the boards.',
        dest='input',
        required=True)
    parser.add_argument(
        '--output', '-o',
        help='directory where to store the result.',
        dest='output',
        required=True)
    args = parser.parse_args()
    for filename in glob(os.path.join(args.input, '*.json')):
        basename = os.path.basename(filename)
        name, ext = os.path.splitext(basename)

        board_description = get_board_description(name=name)
        svg_board = SvgBoardCreator(board_description)
        os.makedirs(args.output, exist_ok=True)

        with open(os.path.join(args.output, name + '.html'), 'w') as svg_output:
            svg_output.write(str(svg_board))
