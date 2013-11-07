#!/usr/bin/env python2
# -*- coding: utf-8 -*-


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


def get_jpegs(path):
    for dirpath, dirnames, files in os.walk(path):
        for f in files:
            if f.endswith('.jpg') or f.endswith('.jpeg'):
                yield os.path.join(dirpath, f)


def get_timestamp(filepath):
    # TODO(ting|#1): fall back to DateTimeDigitized if empty
    # FIXME(ting|#2): handle missing timestamp case
    with open(filepath, 'rb') as f:
        tags = exifread.process_file(
                f,
                details=False,
                stop_tag='EXIF DateTimeOriginal')

    return str(tags['EXIF DateTimeOriginal'])


def parse_args(args):
    if len(args) != 3:
        sys.stderr.write(
                "Usage: %s [input directory] [output directory]\n" % argv[0])
        sys.exit(1)

    if not os.path.isdir(args[1]):
        sys.stderr.write("Invalid directory: %s\n" % args[1])
        sys.exit(1)

    return get_jpegs(args[1]), args[2]


def rename_file(target_dir, input_path):
    dt = timestamp_to_datetime(get_timestamp(input_path))
    output_path = os.path.join(target_dir, datetime_to_path(dt))
    output_dir = os.path.dirname(output_path)

    # create directory in a thread safe fashion
    try:
        os.makedirs(output_dir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    print("%s\n-> %s" % (input_path, output_path))
    shutil.move(input_path, output_path)


def timestamp_to_datetime(string):
    elements = map(int, re.split(':| ', string))
    return datetime.datetime(*elements)


def main(argv=None):
    if not argv:
        argv = sys.argv

    input_paths, output_dir = parse_args(argv)
    rename_files = partial(rename_file, output_dir)
    map(rename_files, input_paths)


if __name__ == "__main__":
    sys.exit(main())
