#! /usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')

import mock

from spider import zhihu_question

class TestZhihuQuestion(unittest.TestCase):

    def setUp(self):
        pass

    @mock.patch("spider.zhihu_question.get_topic_id_seed")
    def test_generate_available_topic_ids(self, mock_get_topic_id_seed):

        mock_get_topic_id_seed.return_value = 1
        actual_str = zhihu_question.generate_available_topic_ids(10, 1)
        expected_str = "1,2,3,4,5,6,7,8,9,10"
        self.assertIsNotNone(actual_str)
        self.assertEqual(expected_str, actual_str)

        mock_get_topic_id_seed.return_value = 2
        actual_str = zhihu_question.generate_available_topic_ids(10, 2)
        expected_str = "2,4,6,8,10"
        self.assertIsNotNone(actual_str)
        self.assertEqual(expected_str, actual_str)

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
