"""
Based on
http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
and
https://github.com/edsu/summoner/blob/master/setup.py
"""

from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main('')
        sys.exit(errno)

setup(
    name = 'vivo-data-management',
    version = '0.0.1',
    url = 'http://github.com/Brown-University-Library/vivo-data-management',
    author = 'Ted Lawless',
    author_email = 'tlawless@brown.edu',
    packages = ['vdm',],
    description = 'Tools for working with data for VIVO.',
    cmdclass = {'test': PyTest},
    install_requires=[
        'requests',
        'bleach',
        'python-dateutil',
        'rdflib>=4.1',
        'rdflib-jsonld>=0.2-dev'
    ],
    dependency_links = [
        'https://github.com/RDFLib/rdflib-jsonld/zipball/master#egg=rdflib-jsonld-0.2-dev'
    ],
    tests_require=['pytest']
)
