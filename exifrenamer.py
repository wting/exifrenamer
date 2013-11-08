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


def create_dir(dirpath):
    # create directory in a thread safe fashion
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


def move_file(src, dst):
    # NOTE(ting|2013-11-07): not thread safe
    while os.path.exists(dst):
        dst = find_alternate_filename(dst)

    print("%s\n-> %s" % (src, dst))
    shutil.move(src, dst)


def parse_args(args):
    if len(args) != 3:
        sys.stderr.write(
                "Usage: %s [input directory] [output directory]\n" % argv[0])
        sys.exit(1)

    for dirpath in args[1:]:
        if not os.path.isdir(dirpath):
            sys.stderr.write("Invalid directory: %s\n" % dirpath)
            sys.exit(1)

    return get_jpegs(args[1]), args[2]


def rename_file(target_dir, input_path):
    try:
        dt = timestamp_to_datetime(get_timestamp(input_path))
    except BadTimestampError:
        print("[ERROR] Invalid timestamp: %s\n" % input_path)
        return
    except MissingTimestampError:
        print("[ERROR] Missing timestamp: %s\n" % input_path)
        return

    output_path = os.path.join(target_dir, datetime_to_path(dt))

    create_dir(os.path.dirname(output_path))
    move_file(input_path, output_path)


def timestamp_to_datetime(string):
    elements = map(int, re.split(':| ', string))

    if len(*elements) != 6:
        raise BadTimestampError

    return datetime.datetime(*elements)


def main(argv=None):
    if not argv:
        argv = sys.argv

    input_paths, output_dir = parse_args(argv)
    rename_files = partial(rename_file, output_dir)
    map(rename_files, input_paths)


if __name__ == "__main__":
    sys.exit(main())
