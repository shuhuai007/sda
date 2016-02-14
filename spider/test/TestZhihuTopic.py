#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append("..")
import zhihu_topic

class TestZhihuAnswer(unittest.TestCase):

    def setUp(self):
        pass

    def test_persist_topics(self):
        topic = zhihu_topic.ZhihuTopic('develop')
        self.assertEqual('develop', topic.mode)
        topic_list = [(5561, 'test-topic', 1)]
        topic.persist_topics(topic_list)
        topic_list = [(5562, 'test-topic', 1)]
        topic.persist_topics(topic_list)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
