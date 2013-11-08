#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
  Copyright © 2009-2013 William Ting

  *  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3, or (at your option)
  any later version.

  *  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  *  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
"""


from __future__ import print_function


import argparse
import datetime
import errno
from functools import partial
import os
import re
import shutil
import sys


import exifread


VERSION = "0.3.0"


class BadTimestampError(Exception):
    pass


class MissingTimestampError(Exception):
    pass


def create_dir(dirpath, simulate=False):
    # create directory in a thread safe fashion
    if simulate:
        return

    try:
        os.makedirs(dirpath)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def datetime_to_path(dt):
    # output: DateTime object -> yyyy/mm/yyyymmdd/yyyymmdd_hhmmss.jpg
    return "%04d/%02d/%02d%02d%02d/%02d%02d%02d_%02d%02d%02d.jpg" % (
            dt.year,
            dt.month,
            dt.year,
            dt.month,
            dt.day,
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second)


def find_alternate_filename(path):
    assert(path.endswith('.jpg'))

    matches = re.search(r'_(?P<count>\d{4}).jpg$', path)

    if not matches:
        return path[:-4] + '_0000.jpg'

    return "%s_%04d.jpg" % (path[:-9], increment(matches.group('count')))


def get_jpegs(path):
    for dirpath, dirnames, files in os.walk(path):
        for f in files:
            if f.endswith('.jpg') or f.endswith('.jpeg'):
                yield os.path.join(dirpath, f)


def get_timestamp(filepath):
    with open(filepath, 'rb') as f:
        tags = exifread.process_file(f, details=False)

    if 'EXIF DateTimeOriginal' in tags:
        return str(tags['EXIF DateTimeOriginal'])
    elif 'EXIF DateTimeDigitized' in tags:
        return str(tags['EXIF DateTimeDigitized'])
    else:
        raise MissingTimestampError


def increment(num):
    return int(num) + 1


def move_file(src, dst, simulate=False):
    # not thread safe
    while os.path.exists(dst):
        dst = find_alternate_filename(dst)

    print("%s\n-> %s" % (src, dst))

    if not simulate:
        shutil.move(src, dst)


def parse_args():
    parser = argparse.ArgumentParser(
            description='Organize and move photos based on timestamp.')
    parser.add_argument('input_dir')
    parser.add_argument('output_dir')
    parser.add_argument(
            '-s',
            '--simulate',
            action='store_true',
            default=False)
    parser.add_argument(
            '-v',
            '--version',
            action='version',
            version='exifrenamer v' + VERSION)
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        sys.stderr.write("Invalid directory: %s\n" % args.input_dir)
        sys.exit(1)

    if not os.path.isdir(args.output_dir):
        sys.stderr.write("Invalid directory: %s\n" % args.output_dir)
        sys.exit(1)

    if args.input_dir == args.output_dir:
        sys.stderr.write("Input and output directories need to be different.\n")
        sys.exit(1)

    if args.simulate:
        print("Simulation...")

    return get_jpegs(args.input_dir), args.output_dir, args.simulate


def rename_file(target_dir, input_path, simulate=False):
    try:
        dt = timestamp_to_datetime(get_timestamp(input_path))
    except BadTimestampError:
        print("[ERROR] Invalid timestamp: %s\n" % input_path)
        return
    except MissingTimestampError:
        print("[ERROR] Missing timestamp: %s\n" % input_path)
        return

    output_path = os.path.join(target_dir, datetime_to_path(dt))
    create_dir(os.path.dirname(output_path), simulate=simulate)
    move_file(input_path, output_path, simulate=simulate)


def timestamp_to_datetime(string):
    elements = map(int, re.split(':| ', string))

    if len(elements) != 6:
        raise BadTimestampError

    return datetime.datetime(*elements)


def main():
    input_paths, output_dir, simulate = parse_args()
    rename_files = partial(rename_file, output_dir, simulate=simulate)
    map(rename_files, input_paths)


if __name__ == "__main__":
    sys.exit(main())
