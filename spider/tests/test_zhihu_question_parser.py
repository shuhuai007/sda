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
    pass


