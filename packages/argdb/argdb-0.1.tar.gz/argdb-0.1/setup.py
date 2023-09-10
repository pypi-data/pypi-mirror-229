#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

exec(open('argdb/version.py').read())

setup(
    name='argdb',
    description='ArgDB - A Datastore for arguments ',
    long_description_content_type="text/markdown",
    long_description="README.md",
    license=license,
    author='Simon Wells',
    url='https://github.com/Open-Argumentation/ArgDB',
    author_email='mail@simonwells.org',
    version=__version__,
    packages=find_packages(exclude=('deploy', 'etc', 'examples'))
)
