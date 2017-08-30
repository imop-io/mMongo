#!/usr/bin/env python

import os
import re
from setuptools import setup

from mmongo import __version__

def _read(pathes):
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        *pathes,
    )
    with open(path, encoding='utf8') as _file:
        return _file.read()

version = re.findall(
    r"^__version__ = '([^']+)'\r?$",
    _read(['mmongo', '__init__.py']),
    re.M
)

setup(
    name='mMongo',
    version=__version__,
    license='https://www.gnu.org/licenses/gpl-3.0.en.html',
    description='A python ODM of mongo based on motor',
    long_description='',
    platforms=('Any'),
    keywords = ["asyncio", "motor", "mongo"],

    author='songww',
    author_email='sww4718168@gmail.com',
    url='https://github.com/ioimop/mMongo',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Natural Language :: Chinese (Simplified)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],

    packages=['mmongo'],
    install_requires=['motor', 'mtypes'],
)
