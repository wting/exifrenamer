#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from setuptools import setup


def get_version(path):
    with open(path) as f:
        for line in f:
            if line.startswith('VERSION'):
                return str(line.split('=')[1]).strip().strip('"')


setup(
    name="exifrenamer",
    license="GPL v3",
    version=get_version('exifrenamer/exifrenamer.py'),
    description="Organize photos based on timestamp metadata.",
    long_description=open('README.md', 'rt').read(),
    author="William Ting",
    author_email="io@williamting.com",
    url="https://github.com/wting/exifrenamer",
    packages=["exifrenamer"],
    install_requires=["exifread >= 1.4.0"],
    scripts={},
    entry_points={
        'distutils.commands': ['flake8 = flake8.main:Flake8Command'],
        'console_scripts': ['flake8 = flake8.main:main'],
        'flake8.extension': [
            'F = flake8._pyflakes:FlakesChecker',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
)
