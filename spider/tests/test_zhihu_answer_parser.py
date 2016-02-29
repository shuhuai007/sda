#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')
from spider.transaction_manager import TransactionManager
from spider import zhihu_answer_parser


class TestZhihuAnswerParser(unittest.TestCase):

    def setUp(self):
        pass

    def test_update_answer(self):
        question_id_list = [19575624]
        tm = TransactionManager()
        zhihu_answer_parser.update_answer(question_id_list, tm)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
