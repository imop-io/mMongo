#!/usr/bin/env python

from setuptools import setup

from mmongo import _version

setup(
    name='mMongo',
    version=_version,
    license='https://www.gnu.org/licenses/gpl-3.0.en.html',
    description='A python ODM of mongo based on motor',
    long_description='',
    platforms=('Any'),
    keywords = ["asyncio", "motor", "mongo"]

    author='songww',
    author_email='sww4718168@gmail.com',
    url='https://github.com/ioimop/mMongo',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv3 License',
        'Natural Language :: English',
        'Natural Language :: Chinese',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],

    py_modules=['mmongo'],
    install_requires=['motor'],
)
