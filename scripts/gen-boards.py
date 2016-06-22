################################################################################
# Copyright (C) 2015-2016 by Arena of Titans Contributors.
#
# This file is part of Arena of Titans.
#
# Arena of Titans is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Arena of Titans is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
################################################################################

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
