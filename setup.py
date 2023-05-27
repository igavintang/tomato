#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys
from setuptools import setup, find_packages


if sys.version_info < (3, 5, 3):
    raise RuntimeError('aiohttp 3.x requires Python 3.5.3+')

with open('requirements.txt') as f:
    requirements = [l for l in f.read().splitlines() if l]

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setup(
    name = 'tomato',
    version = '0.0.1',
    test_suite='nose.collector',
    tests_require=['nose'],
    packages = find_packages(),
    install_requires = requirements,
    author='Gavin Tang',
    author_email='gavintang@pm.me',
    maintainer='Gavin Tang <gavintang@pm.me>',
    maintainer_email='gavintang@pm.me',
    description = 'A quick and lightweight server framework.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    data_files=[
        ('requires', ['requirements.txt']),
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: AsyncIO',
    ],
    python_requires='>=3.5.3',
    url='https://github.com/igavintang/tomato',
    license="GNU General Public License v3",
    keywords = ['tomato', 'python']
)
