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

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            'aot/test',
            '--cov',
            'aot',
            '--cov-report',
            'html',
            '--cov-config',
            '.coveragerc',
            '--ignore',
            'aot/test/integration/'
        ]
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)


with open('requires.txt', 'r') as requires:
    install_requires = requires.read().split('\n')


with open('tests_requires.txt', 'r') as requires:
    tests_require = requires.read().split('\n')


setup(
    name='Arena of Titans - API',
    version='0.1',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    author='jenselme',
    author_email='contact@arenaoftitans.com',
    url='https://bitbucket.org/arenaoftitans/arena-of-titans-api',
    license='GNU AGPL',
)
