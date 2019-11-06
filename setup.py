# setup.py
from distutils.core import setup

from setuptools import find_packages

setup(
    name='interview',
    version='0.0.1',
    author='Seth Widoff',
    author_email='swidoff@gmail.com',
    url='https://github.com/swidoff/interview',
    packages=find_packages(),
    package_data={'interview': ['*.ipnyb', 'data/*.db'], }
)
