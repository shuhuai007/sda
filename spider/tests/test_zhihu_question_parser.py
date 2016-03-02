#! /usr/bin/env python
# coding=utf-8


import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/..')
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')

import mock

from spider import zhihu_question_parser
from spider import zhihu_constants
from spider import zhihu_util


class TestZhihuQuestionParser(unittest.TestCase):

    def setUp(self):
        self.sample_topic_id = "19551296"
        self.question_data_file = "19551296_question.data"

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

    def test_write_question(self):
        question_list = [(40899135, "问道那个区现在人最火爆?", 908, 0, "2016-03-01 10:53:57"),
                         (40899078, "为什么lol有人拿四杀幸存的那个人会跑得那么快？", 0, 0, "2016-03-01 10:53:57")
                         ]
        zhihu_question_parser.write_question(question_list, self.sample_topic_id, ".")
        with open(self.question_data_file, "r") as f:
            lines = f.readlines()
        self.assertIsNotNone(lines)
        self.assertEqual(2, len(lines))

        first_line_list = lines[0].split(zhihu_constants.ZHIHU_QUESTION_DATA_DELIMETER)
        self.assertEqual(5, len(first_line_list))

    @mock.patch("spider.zhihu_question_parser.get_question_data_directory")
    def test_fetch_question_list_per_topic(self, mock_get_question_data_directory):
        mock_get_question_data_directory.return_value = "."
        zhihu_question_parser.fetch_question_list_per_topic(self.sample_topic_id, True)
        with open(self.question_data_file, "r") as f:
            lines = f.readlines()
        self.assertIsNotNone(lines)
        self.assertTrue(len(lines) <= 20)

        self.assertTrue(len(lines[0].split(zhihu_constants.ZHIHU_QUESTION_DATA_DELIMETER)) == 5)

    def test_get_max_page_index(self):
        list_question_url = "https://www.zhihu.com/topic/19552397/questions?page=1"
        max_id = zhihu_question_parser.get_max_page_index(list_question_url)
        self.assertTrue(max_id > 1)

    def test_generate_question_list_per_page(self):
        list_question_url = "https://www.zhihu.com/topic/19552397/questions?page=2"
        resp = zhihu_util.get_content(list_question_url)
        question_list = zhihu_question_parser.generate_question_list_per_page(resp)
        self.assertTrue(len(question_list) > 0)

        self.assertTrue(len(question_list) <= 20)

    def tearDown(self):
        if os.path.exists(self.question_data_file):
            os.remove(self.question_data_file)


if __name__ == "__main__":
    unittest.main()
