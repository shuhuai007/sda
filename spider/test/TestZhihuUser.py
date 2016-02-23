#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')
from spider.entity import zhihu_user

import unittest


class TestZhihuUser(unittest.TestCase):

    def setUp(self):
        url = "http://www.zhihu.com/people/jie-28"
        self._user = zhihu_user.User(url)
        pass

    def test_generate_user_seed(self):
        user_seeds = self._user.generate_user_seeds(1)
        self.assertEqual(len(user_seeds), 1*3)

        print user_seeds

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
