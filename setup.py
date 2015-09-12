#!/usr/bin/env python3

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--cov',
            'aot',
            '--cov-report',
            'html',
            '--cov-config',
            '.coveragerc',
            '--ignore',
            'aot/test/integration/test_api.py'
        ]
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)


setup(
    name='Arena of Titans - API',
    version='0.1',
    packages=find_packages(),
    install_requires=['aiohttp', 'autobahn', 'lxml', 'redis', 'toml'],
    tests_require=['pytest', 'pytest-asyncio', 'pytest-cov', 'requests', 'websockets'],
    cmdclass={'test': PyTest},
    author='jenselme',
    author_email='',
    url='',
    license='',
)
