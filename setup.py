#!/usr/bin/env python3

from setuptools import setup


setup(
    name='dj-tables',
    version='0.0.0',
    description='Template only, DRY solution for creating tables using Django',
    author='Zach Perkitny',
    author_email='zperkitny@gmail.com',
    url='https://dj-tables.readthedocs.io/en/latest/',
    packages=['dj_tables'],
    install_requires=['Django>=2.0.0'])
