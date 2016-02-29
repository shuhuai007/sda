#! /usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')

from spider import zhihu_question

class TestZhihuQuestion(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
