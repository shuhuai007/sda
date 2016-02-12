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
        print "......"
        self.assertTrue(response != "FAIL")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
