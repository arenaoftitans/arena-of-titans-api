#!/usr/bin/env python3

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


with open('tests_require.txt', 'r') as requires:
    tests_require = requires.read().split('\n')


setup(
    name='Arena of Titans - API',
    version='0.1',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    author='jenselme',
    author_email='',
    url='',
    license='',
)
