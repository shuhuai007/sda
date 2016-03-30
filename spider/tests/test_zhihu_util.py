#! /usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')
from spider import zhihu_util


class TestZhihuUtil(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_content(self):
        request_url = "https://www.zhihu.com/topic/19551557/questions"
        response = zhihu_util.get_content(request_url)
        self.assertTrue(response != "FAIL")

    def test_get_content_repeatedly(self):
        count = 0
        request_url = "https://www.zhihu.com/topic/19551557/questions"
        while count < 3:
            response = zhihu_util.get_content(request_url)
            print "...get content count:%s" % count
            self.assertTrue(response != "FAIL", "get content count is {0}".format(count))
            count += 1

    def test_post(self):
        post_url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
        post_data = 'method=next&params=%7B%22topic_id%22%3A253%2C%22offset%22%3A60%2C%22hash_id%22%3A%22dced108689287057f5cc3b5e85cb8289%22%7D&_xsrf=c6946d5914172133e875956a711be3ad'
        zhihu_util.post(post_url, post_data)

    def test_post_repeatedly(self):
        count = 0
        post_url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
        post_data = 'method=next&params=%7B%22topic_id%22%3A686%2C%22offset%22%3A80%2C%22hash_id%22%3A%22dced108689287057f5cc3b5e85cb8289%22%7D&_xsrf=c6946d5914172133e875956a711be3ad'

        while count < 3:
            response = zhihu_util.post(post_url, post_data)
            print "...post count:%s" % count
            self.assertTrue(response != "FAIL", "post count is {0}".format(count))
            count += 1

    def test_get_question_data_directory(self):
        question_data_dir = zhihu_util.get_question_data_directory()
        self.assertTrue(os.path.exists(question_data_dir))

        self.assertTrue("sda/data/zhihu/question" in question_data_dir)

    def test_get_answer_data_directory(self):
        answer_data_dir = zhihu_util.get_answer_data_directory()
        self.assertTrue(os.path.exists(answer_data_dir))
        self.assertTrue("sda/data/zhihu/answer" in answer_data_dir)

    def test_get_data_directory(self):
        answer_data_dir = zhihu_util.get_data_directory("answer")
        self.assertTrue(os.path.exists(answer_data_dir))
        self.assertTrue("sda/data/zhihu/answer" in answer_data_dir)

        question_data_dir = zhihu_util.get_data_directory("question")
        self.assertTrue(os.path.exists(question_data_dir))

        self.assertTrue("sda/data/zhihu/question" in question_data_dir)


    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
