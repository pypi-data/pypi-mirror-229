#!/usr/bin/env python

from io import open
from setuptools import setup

"""
:authors: Peopl3s
:license: Apache License, Version 2.0, see LICENSE file
:copyright: (c) 2021 Peopl3s
"""

version = '1.0.0'

setup(
    name='mini-abuze',
    version=version,

    author='Vaddos',
    author_email='vladomaksb@gmail.com',

    description=(
        u'Python module for writing scripts for project management platform '
        u'Club House (clubhouse.io API wrapper)'
    ),

    url='https://github.com/vaddos689/mini-abuze',
    download_url='https://github.com/vaddos689/mini-abuze/archive/refs/heads/main.zip',

    license='Apache License, Version 2.0, see LICENSE file',

    packages=['mini-abuze'],
    install_requires=['loguru', 'tls-client'],

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)