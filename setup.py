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

from setuptools import (
    find_packages,
    setup,
)
from setuptools.command.test import test as TestCommand  # noqa: N812


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        import sys
        errno = pytest.main(self.test_args)
        sys.exit(errno)


requires = []


setup(
    name='Arena of Titans - API',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    cmdclass={'test': PyTest},
    entry_points={
        'console_scripts': [
            'aot-api = aot.__main__:main',
        ],
    },
    author='jenselme',
    author_email='contact@arenaoftitans.com',
    url='https://gitlab.com/arenaoftitans/arena-of-titans-api',
    license='GNU AGPL',
)
