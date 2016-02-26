#! /usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/..')

import unittest
import mock

import spider.zhihu_topic
import spider.zhihu_util


class TestZhihuTopic(unittest.TestCase):

    def setUp(self):
        pass

    @mock.patch('spider.zhihu_util.get_xsrf')
    def test_generate_post_data(self, mock_get_xsrf):
        hash_id, level1_topic_id, offset = ("dced108689287057f5cc3b5e85cb8289", "253", "40")
        mock_get_xsrf.return_value = "81d4317bc49ba8e6a35c9a9da4c7c58f"

        expected_value = "_xsrf=81d4317bc49ba8e6a35c9a9da4c7c58f&" \
                         "params=%7B%22topic_id%22%3A253%2C%22offset%22%3A40%2C%22hash_id%22%3A%22dced108689287057f5cc3b5e85cb8289%22%7D&" \
                         "method=next"
        actual_value = spider.zhihu_topic.generate_post_data(hash_id, level1_topic_id, offset)
        self.assertEqual(expected_value, actual_value)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
