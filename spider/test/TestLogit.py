#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')
from spider.utils import logit


class TestUtil(unittest.TestCase):

    def setUp(self):
        @logit.logit("test.log")
        def func1():
            pass
        self.example_func = func1

    def test_get_content(self):
        self.example_func()
        self.assertTrue(os.path.exists("test.log"))

    def tearDown(self):
        os.remove("test.log")


if __name__ == '__main__':
    unittest.main()
