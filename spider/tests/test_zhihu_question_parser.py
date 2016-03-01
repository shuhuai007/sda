#! /usr/bin/env python
# -*- code: utf-8 -*-


import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/..')
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')

import mock

from spider import zhihu_question_parser


class TestZhihuQuestionParser(unittest.TestCase):

    def setUp(self):
        pass

    @mock.patch("spider.zhihu_question_parser.get_page_count_percentage")
    def test_get_page_index_threshold(self, mock_get_page_count_percentage):

        mock_get_page_count_percentage.return_value = 0.2
        actual_result = zhihu_question_parser.get_page_index_threshold(10, True)
        self.assertEqual(1, actual_result)
        actual_result = zhihu_question_parser.get_page_index_threshold(10, False)
        self.assertEqual(2, actual_result)

        mock_get_page_count_percentage.return_value = 0.83
        actual_result = zhihu_question_parser.get_page_index_threshold(100, False)
        self.assertEqual(83, actual_result)
        actual_result = zhihu_question_parser.get_page_index_threshold(9, False)
        self.assertEqual(8, actual_result)

    def test_transfer_timestamp(self):
        time_format = "%Y-%m-%d %H:%M:%S"
        import time
        actual_time_str = zhihu_question_parser.transfer_timestamp(time.time() * 1000, time_format)
        self.assertEqual(2, len(actual_time_str.split(" ")))

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
