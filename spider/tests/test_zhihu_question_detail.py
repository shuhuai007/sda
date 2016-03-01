#! /usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/..')
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')

import mock

from spider import zhihu_question_detail


class TestZhihuQuestionDetail(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_question_id_list(self):
        question_id_list = zhihu_question_detail.get_question_id_list()
        self.assertTrue(len(question_id_list) > 0)

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
