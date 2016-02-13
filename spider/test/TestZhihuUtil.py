#! /usr/bin/env python
# -*- coding: utf-8 -*-



import unittest
import sys
sys.path.append("..")
import zhihu_util

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
        while count < 10:
            response = zhihu_util.get_content(request_url)
            print "...count:%s" % count
            self.assertTrue(response != "FAIL", "count is {0}".format(count))
            count += 1

    def test_post(self):
        post_url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
        post_data = 'method=next&params=%7B%22topic_id%22%3A686%2C%22offset%22%3A80%2C%22hash_id%22%3A%22dced108689287057f5cc3b5e85cb8289%22%7D&_xsrf=81d4317bc49ba8e6a35c9a9da4c7c58f'
        zhihu_util.post(post_url, post_data)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
