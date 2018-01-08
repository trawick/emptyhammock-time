#!/usr/bin/env python3

import os
import sys

from setuptools import find_packages, setup

import e_contact

VERSION = e_time.__version__

if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    os.system("git push --tags")
    sys.exit()

setup(
    name='emptyhammock_time',
    packages=find_packages(),
    include_package_data=True,
    license='Apache 2.0 License',
    version=VERSION,
    description='A Python library providing time-relatged utility',
    author='Emptyhammock Software and Services LLC',
    author_email='info@emptyhammock.com',
    url='https://github.com/trawick/emptyhammock-time',
    classifiers=[
        'License :: OSI Approved :: Apache 2.0 License',
        'Development Status :: 3 - Alpha',
    ],
)
