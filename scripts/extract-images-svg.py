#!/usr/bin/env python3

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


import sys

from base64 import b64decode
from lxml import etree


NS = {
    'svg': 'http://www.w3.org/2000/svg',
    'xlink': 'http://www.w3.org/1999/xlink',
}


def print_help():
    print('./extract-images-svg.py SVG_FILE')
    print('This will extract the images included in b64 in the SVG.')


def extract_images_svg(file_name):
    with open(file_name) as svg_file:
        svg = etree.parse(svg_file)

    images = svg.xpath('.//svg:image', namespaces=NS)
    for index, img in enumerate(images):
        content = img.get('{http://www.w3.org/1999/xlink}href')
        if content.startswith('data:image/'):
            meta, img_b64 = content.split(';base64,')
            _, img_format = meta.split('/')
            img_file_name = 'img-{index}.{format}'.format(index=index, format=img_format)
            img.set('{http://www.w3.org/1999/xlink}href', img_file_name)
            with open(img_file_name, 'wb') as img_file:
                img_file.write(b64decode(img_b64))

    with open('svg-without-images.svg', 'w') as svg_file:
        svg_content = etree.tostring(svg)\
                .decode('utf-8')\
                .replace('&gt;', '>')
        svg_file.write(svg_content)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print_help()
        sys.exit(0)

    extract_images_svg(sys.argv[1])
