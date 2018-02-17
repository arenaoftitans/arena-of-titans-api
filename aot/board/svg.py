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

import xml.etree.ElementTree as ET  # noqa: B405 (xml from stdlib can be a security risk)

from .board import get_colors_disposition


ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('cc', 'http://creativecommons.org/ns#')
ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
ET.register_namespace('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')


class SvgBoardCreator:
    #: XML namespace. Required to use xpath to search the DOM.
    NS = {'ns': 'http://www.w3.org/2000/svg'}
    _LAST_LINE_CLASS_TEMPLATE = "${{playerIndex == {} ? 'last-line-square' : ''}}"
    _SQUARE_ID_TEMPLATE = 'square-{}-{}'
    _ARRIVAL_SPOT_CLASS_TEMPLATE = 'arrival arrival-{index}'
    _PAWN_CLASS_TEMPLATE = r"${{playerIndexes.indexOf({index}) === -1 ? 'hidden' : ''}} ${{isPawnClickable[{index}] ? 'pointer' : ''}}"  # noqa
    _PAWN_DELETAGE_TEMPLATE = '{attr}.delegate'
    _PAWN_DELETAGE_TEMPLATES = {
        'click': 'pawnClicked({index})',
        'mouseover': 'showPlayerName({index}, $event)',
        'mouseout': 'hidePlayerName()',
    }
    _PLAY_ATTR_TEMPLATE = "moveTo('{}', '{}', '{}')"
    _SQUARE_CLASS_TEMPLATE = "square {} ${{possibleSquares.indexOf('{}') > -1 ? 'highlighted-square' : ''}}"  # noqa
    _TRANSFORM = 'transform'
    _TEMPLATE_LOCATION = 'aot/resources/templates/boards/standard.html'

    def __init__(self, board_description):
        self._xid = 0
        self._yid = 0
        self._number_arms = board_description['number_arms']
        self._colors_disposition = get_colors_disposition(
            board_description['arms_colors'],
            board_description['inner_circle_colors'],
            board_description['number_arms'])
        self._arms_width = board_description['arms_width']
        self._arms_length = board_description['arms_length']

        self._svg, self._board_layer, self._pawn_layer = self._load_template()
        self._create_svg_board()

    def _load_template(self):
        with open(self._TEMPLATE_LOCATION, 'r') as template_file:
            svg = ET.parse(template_file)  # noqa: B314 (ET usage)
            pawn_layer = svg.findall(
                './/ns:g[@id="pawnLayer"]',
                namespaces=self.NS)[0]
            board_layer = svg.findall(
                './/ns:g[@id="boardLayer"]',
                namespaces=self.NS)[0]
            return svg, board_layer, pawn_layer

    def _create_svg_board(self):
        self._setup_board_layer()
        self._setup_arrival_line()
        self._setup_pawn_layer()

    def _get_id(self, x, y):
        return self._SQUARE_ID_TEMPLATE.format(x, y)

    def _set_click_attr(self, element, x, y):
        square_id = self._get_id(x, y)
        click_attr = self._PLAY_ATTR_TEMPLATE.format(square_id, x, y)
        element.set('click.delegate', click_attr)

    def _setup_board_layer(self):
        for y, line in enumerate(self._colors_disposition):
            for x in range(len(line)):
                path = './/*[@id="square-{}-{}"]'.format(x, y)
                square = self._svg.findall(path, namespaces=self.NS)[0]
                self._set_click_attr(square, x, y)
                color = self._colors_disposition[y][x]
                svg_color = color.lower()
                primary_class = svg_color + '-square'
                square_id = self._get_id(x, y)
                class_ = self._SQUARE_CLASS_TEMPLATE.format(primary_class, square_id)
                if self._is_on_last_line(y):
                    class_ += ' ' + self._last_line_class(x)
                square.set('class', class_)

    def _is_on_last_line(self, y):
        return y == 8

    def _last_line_class(self, x):
        index = -1
        if 0 <= x <= 3:
            index = 4
        elif 4 <= x <= 7:
            index = 5
        elif 8 <= x <= 11:
            index = 6
        elif 12 <= x <= 15:
            index = 7
        elif 16 <= x <= 19:
            index = 0
        elif 20 <= x <= 23:
            index = 1
        elif 24 <= x <= 27:
            index = 2
        elif 28 <= x <= 31:
            index = 3

        return self._LAST_LINE_CLASS_TEMPLATE.format(index)

    def _setup_arrival_line(self):
        arrival_layer = self._board_layer.findall(
            './/ns:g[@id="arrivalLayer"]',
            namespaces=self.NS,
        )[0]
        for index, arrival_spot in enumerate(arrival_layer):
            arrival_spot.set('class', self._ARRIVAL_SPOT_CLASS_TEMPLATE.format(index=index))

    def _setup_pawn_layer(self):
        for index, pawn in enumerate(self._pawn_layer):
            pawn.set('class', self._PAWN_CLASS_TEMPLATE.format(index=index))
            for attr, value in self._PAWN_DELETAGE_TEMPLATES.items():
                pawn.set(
                    self._PAWN_DELETAGE_TEMPLATE.format(attr=attr),
                    value.format(index=index),
                )

    @property
    def svg(self):  # pragma: no cover
        return self._svg

    def __str__(self):
        return ET.tostring(self._svg.getroot())\
            .decode('utf-8')\
            .replace('&gt;', '>')

    def __repr__(self):  # pragma: no cover
        return str(self)
