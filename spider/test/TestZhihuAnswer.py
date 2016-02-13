#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append("..")
import zhihu_answer

class TestZhihuAnswer(unittest.TestCase):

    def setUp(self):
        pass

    def test_generate_question_id_list(self):
        answer = zhihu_answer.ZhihuAnswer('develop')
        print "mode:%s" % answer.mode
        question_id_list = answer.generate_question_id_list('2016-01-01')
        self.assertIsNotNone(question_id_list)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
