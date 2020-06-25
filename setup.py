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
    version = '0.0.3',
    url = 'http://github.com/Brown-University-Library/vivo-data-management',
    author = 'Brown University Library',
    author_email = 'bdr@brown.edu',
    packages = ['vdm',],
    description = 'Tools for working with data for VIVO.',
    cmdclass = {'test': PyTest},
    install_requires=[
        'requests==2.7.0',
        'bleach==1.4.2',
        'html5lib==0.9999999',
        'nameparser==0.3.9',
        'python-dateutil==2.4.2',
        'rdflib==4.2.2',
        'rdflib-jsonld<0.5.0',
        'SPARQLWrapper==1.8.5',
    ],
    extras_require={
        'test': ['pytest==2.6.4', 'responses==0.10.6']
    }
)
