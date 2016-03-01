#! /usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/..')
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')

from spider import zhihu_answer_parser


class TestZhihuAnswerParser(unittest.TestCase):

    def setUp(self):
        pass

    def test_update_answer(self):
        pass

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
