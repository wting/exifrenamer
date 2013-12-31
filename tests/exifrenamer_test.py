#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from testify import *

from exifrenamer import find_alternate_filename
from exifrenamer import increment


class HelpersTestCase(TestCase):

    def test_increment(self):
        assert_equal(increment(0), 1)

    def test_good_fan_filenames(self):
        assert_equal(find_alternate_filename('foo.jpg'), 'foo-0000.jpg')


if __name__ == "__main__":
    run()
