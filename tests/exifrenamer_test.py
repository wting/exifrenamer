#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from testify import *

from exifrenamer import increment


class HelpersTestCase(TestCase):

    @class_setup
    def init(self):
        self.var = 0

    def test_increment(self):
        assert_equal(increment(0), 1)


if __name__ == "__main__":
    run()
