#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from exifrenamer import find_alternate_filename
from exifrenamer import increment


def test_increment():
    assert increment(0) == 1


def test_good_fan_filenames():
    assert find_alternate_filename('foo.jpg') == 'foo-0000.jpg'
