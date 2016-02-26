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
        squre_url = "https://www.zhihu.com/topics"
        self.topic_square = spider.zhihu_topic.ZhihuTopicSquare(squre_url)
        self.topic_level1_sample = spider.zhihu_topic.ZhihuLevel1Topic('253', '游戏', '253', 'sdfad')

    @mock.patch('spider.zhihu_util.get_xsrf')
    def test_generate_post_data(self, mock_get_xsrf):
        hash_id, level1_topic_id, offset = ("dced108689287057f5cc3b5e85cb8289", "253", "40")
        mock_get_xsrf.return_value = "81d4317bc49ba8e6a35c9a9da4c7c58f"

        expected_value = "_xsrf=81d4317bc49ba8e6a35c9a9da4c7c58f&" \
                         "params=%7B%22topic_id%22%3A253%2C%22offset%22%3A40%2C%22hash_id%22%3A%22dced108689287057f5cc3b5e85cb8289%22%7D&" \
                         "method=next"
        actual_value = spider.zhihu_topic.generate_post_data(hash_id, level1_topic_id, offset)
        self.assertEqual(expected_value, actual_value)

    def test_get_topic_id(self):
        self.assertEqual("253", self.topic_level1_sample.get_topic_id())

    def test_get_parent_id(self):
        self.assertEqual("253", self.topic_level1_sample.get_parent_id())

    def test_get_topic_name(self):
        self.assertEqual("游戏", self.topic_level1_sample.get_topic_name())

    def test_get_fileds(self):
        expected_fields = ("253", "游戏", "253")
        self.assertEqual(expected_fields, self.topic_level1_sample.get_fields())

    def test_get_level1_topics(self):
        level1_topics = list(self.topic_square.get_level1_topics())
        self.assertTrue(len(level1_topics) > 0)
        self.assertTrue(len(level1_topics) >= 33)
        self.assertTrue(isinstance(level1_topics[0], spider.zhihu_topic.ZhihuTopic))
        self.assertIsNotNone(level1_topics[0].get_topic_id())
        self.assertIsNotNone(level1_topics[0].get_topic_name())
        self.assertIsNotNone(level1_topics[0].get_parent_id())

    def test_get_level2_topics(self):
        level2_topics = self.topic_level1_sample.get_level2_topics()
        self.assertTrue(len(level2_topics) >= 0)

        self.assertTrue(isinstance(level2_topics[0], spider.zhihu_topic.ZhihuTopic))
        self.assertNotEqual(level2_topics[0].get_parent_id(), level2_topics[0].get_topic_id())


    def test_get_topics(self):
        pass

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
