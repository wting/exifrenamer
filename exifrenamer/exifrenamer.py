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
from itertools import tee
import os
import re
import shutil
import sys


import exifread


VERSION = "0.3.1"


class BadTimestampError(Exception):
    pass


class MissingTimestampError(Exception):
    pass


def check_overwrite_collisions(input_paths):
    seen = set()

    for path in input_paths:
        try:
            dt = timestamp_to_datetime(get_timestamp(path))
            if dt in seen:
                print("[ERROR] Duplicate timestamps detected, --overwrite \
                        will result in loss of photos: %s" % path)
                sys.exit(2)
            seen.add(dt)
        except BadTimestampError:
            print("[ERROR] Invalid timestamp: %s\n" % path)
            continue
        except MissingTimestampError:
            print("[ERROR] Missing timestamp: %s\n" % path)
            continue


def create_dir(args, dirpath):
    # create directory in a thread safe fashion
    if args.simulate:
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

    matches = re.search(r'-(?P<count>\d{4}).jpg$', path)

    if not matches:
        return path[:-4] + '-0000.jpg'

    return "%s-%04d.jpg" % (path[:-9], increment(matches.group('count')))


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


def move_file(args, src, dst):
    # not thread safe
    while not args.overwrite and os.path.exists(dst):
        dst = find_alternate_filename(dst)

    print("%s\n-> %s" % (src, dst))

    if not args.simulate:
        shutil.move(src, dst)


def parse_args():
    parser = argparse.ArgumentParser(
            description='Organize and move photos based on timestamp.')
    parser.add_argument('input_dir')
    parser.add_argument('output_dir')
    parser.add_argument(
            '-o',
            '--overwrite',
            action='store_true',
            default=False)
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

    return get_jpegs(args.input_dir), args


def rename_file(args, input_path):
    try:
        dt = timestamp_to_datetime(get_timestamp(input_path))
    except BadTimestampError:
        print("[ERROR] Invalid timestamp: %s\n" % input_path)
        return
    except MissingTimestampError:
        print("[ERROR] Missing timestamp: %s\n" % input_path)
        return

    output_dir = os.path.join(args.output_dir, datetime_to_path(dt))
    create_dir(args, os.path.dirname(output_dir))
    move_file(args, input_path, output_dir)


def timestamp_to_datetime(string):
    elements = map(int, re.split(':| ', string))

    if len(elements) != 6:
        raise BadTimestampError

    return datetime.datetime(*elements)


def main():
    input_paths, args = parse_args()
    it1, it2 = tee(input_paths)
    rename_files = partial(rename_file, args)

    if args.overwrite:
        check_overwrite_collisions(it2)

    map(rename_files, it1)


if __name__ == "__main__":
    sys.exit(main())
