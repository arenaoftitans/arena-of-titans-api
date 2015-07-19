#!/usr/bin/env python3

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--cov', 'aot', '--cov-report', 'html']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)


setup(
    name='aot',
    version='0.1',
    packages=find_packages(),
    install_requires=['autobahn', 'redis'],
    tests_require=['pytest', 'pytest-cov'],
    cmdclass={'test': PyTest},
    author='jenselme',
    author_email='',
    url='',
    license='',
)
