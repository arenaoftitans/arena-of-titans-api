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
# along with Arena of Titans. If not, see <http://www.GNU Affero.org/licenses/>.
################################################################################

from lxml import etree

from aot.board import get_colors_disposition


class SvgBoardCreator:
    #: XML namespace. Required to use xpath to search the DOM.
    NS = {'ns': 'http://www.w3.org/2000/svg'}
    _SQUARE_ID_TEMPLATE = 'square-{}-{}'
    _ROTATE_TEMPLATE = 'rotate({} {} {})'
    _NG_PLAY_ATTR_TEMPLATE = "moveTo('{}', '{}', '{}')"
    _TRANSFORM = 'transform'
    _TEMPLATE_LOCATION = 'aot/resources/templates/boards/standard.html'

    def __init__(self, board_description):
        svg = board_description['svg']
        self._xid = 0
        self._yid = 0
        self._number_arms = board_description['number_arms']
        self._colors_disposition = get_colors_disposition(
            board_description['arms_colors'],
            board_description['inner_circle_colors'],
            board_description['number_arms'])
        self._arms_width = board_description['arms_width']
        self._arms_length = board_description['arms_length']
        self._x_origin, self._y_origin = svg['fill_origin']
        self._rotation_x, self._rotation_y = svg['rotation_center']
        self._lines = svg['lines']
        self._fill_element_width = svg['fill']['width']
        self._fill_element_height = svg['fill']['height']
        self._fill_element_tag = svg['fill']['tag']

        self._svg, self._board_layer, self._pawn_layer = self._load_template()
        self._create_svg_board()

    def _load_template(self):
        with open(self._TEMPLATE_LOCATION, 'r') as template_file:
            svg = etree.parse(template_file)
            pawn_layer = svg.xpath(
                './/ns:g[@id="pawnLayer"]',
                namespaces=self.NS)[0]
            board_layer = svg.xpath(
                '//ns:g[@id="boardLayer"]',
                namespaces=self.NS)[0]
            return svg, board_layer, pawn_layer

    def _create_svg_board(self):
        for _ in range(self._number_arms):
            self._rotate_board()
            self._draw_lines()
            self._fill_svg()

        self._rotate_board()
        self._paint_svg()

    def _rotate_board(self):
        delta_angle = int(360 / self._number_arms)
        for element in self._board_layer:
            if element.get(self._TRANSFORM):
                transformation = element.get('transform')
                if transformation[9] == ' ':
                    angle = int(transformation[7:9])
                else:
                    angle = int(transformation[7:10])
                angle += delta_angle
            else:
                angle = delta_angle
            transformation = self._ROTATE_TEMPLATE.format(
                angle,
                self._rotation_x,
                self._rotation_y)
            element.set(self._TRANSFORM, transformation)

    def _draw_lines(self):
        self._yid = 0
        for line in self._lines:
            xid_delta = 0
            for element in line:
                current_xid = self._xid + xid_delta
                svg_element = etree.SubElement(
                    self._board_layer,
                    element['tag'])
                svg_element.set('d', element['d'])
                self._set_id(svg_element, current_xid, self._yid)
                self._set_ng_click_attr(svg_element, current_xid, self._yid)
                self._board_layer.append(svg_element)
                xid_delta += 1
            self._yid += 1

    def _get_id(self, x, y):
        return self._SQUARE_ID_TEMPLATE.format(x, y)

    def _set_id(self, element, x, y):
        element.set('id', self._get_id(x, y))

    def _set_ng_click_attr(self, element, x, y):
        square_id = self._get_id(x, y)
        ng_click_attr = self._NG_PLAY_ATTR_TEMPLATE.format(square_id, x, y)
        element.set('click.delegate', ng_click_attr)

    def _fill_svg(self):
        delta_xid = 0
        for i in range(self._arms_width):
            self._yid = len(self._lines)
            for j in range(self._arms_length):
                current_xid = self._xid + delta_xid
                x = i * self._fill_element_height + self._x_origin
                y = j * self._fill_element_width + self._y_origin
                element = etree.SubElement(
                    self._board_layer,
                    self._fill_element_tag)
                self._set_id(element, current_xid, self._yid)
                element.set('x', str(x))
                element.set('y', str(y))
                element.set('height', str(self._fill_element_height))
                element.set('width', str(self._fill_element_width))
                self._set_ng_click_attr(element, current_xid, self._yid)
                self._yid += 1
                self._board_layer.append(element)
            delta_xid += 1
        self._xid += self._arms_width

    def _paint_svg(self):
        for y, line in enumerate(self._colors_disposition):
            for x in range(len(line)):
                path = './/*[@id="square-{}-{}"]'.format(x, y)
                square = self._svg.xpath(path, namespaces=self.NS)[0]
                color = self._colors_disposition[y][x]
                svg_color = color.value.lower()
                primary_class = svg_color + '-square'
                square_id = self._get_id(x, y)
                class_template = \
                    "{} ${{_possibleSquares.indexOf('{}') > -1 ? 'highlightedSquare' : ''}}"
                ng_class = class_template.format(primary_class, square_id)
                square.set('class', ng_class)

    @property
    def svg(self):  # pragma: no cover
        return self._svg

    def __str__(self):
        return etree.tostring(self._svg)\
            .decode('utf-8')\
            .replace('&gt;', '>')

    def __repr__(self):  # pragma: no cover
        return etree.tostring(self._svg, pretty_print=True)\
            .decode('utf-8')\
            .replace('&gt;', '>')
