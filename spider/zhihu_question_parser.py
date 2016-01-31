#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt
import MySQLdb
from bs4 import BeautifulSoup
import json
import re
import time
from math import ceil
import logging
import threading
import Queue
import ConfigParser

from zhihu_constants import *

from urllib import urlencode

from zhihu_util import get_content
from zhihu_util import post
from zhihu_util import get_xsrf_from_cookie
from zhihu_util import get_xsrf

LIST_QUESITON_PAGE_COUNT_PERCENTAGE=1

def fetch_question_list(level2_topic_id_list):
    question_list = []
    # 1. list all the questions for each level2 topic.
    for level2_topic_id in level2_topic_id_list:
        temp_question_list = fetch_question_list_per_topic(level2_topic_id)
        question_list += temp_question_list

    print "\n......question_list:%s" % question_list
    # 2. update the list created by 1st step
    # URL-https://www.zhihu.com/question/40009083
    # TODO add logic

    return question_list

def fetch_question_list_per_topic(level2_topic_id):
    temp_question_list = []
    # TODO(zj) add logic
    # URL-https://www.zhihu.com/topic/19552397/questions?page=1
    max_page_index = get_max_page_index()
    print "\n......max page index:%s" % max_page_index

    page_index = 1
    while page_index <= int(round(LIST_QUESITON_PAGE_COUNT_PERCENTAGE * max_page_index)):
        print "......enter while loop"
        list_question_url = "https://www.zhihu.com/topic/19550994/questions?page=1"
        resp = get_content(list_question_url)
        print "......resp:%s" % resp
        question_list_per_page = generate_question_list_per_page(resp)
        temp_question_list += question_list_per_page
        page_index += 1
    return temp_question_list

def get_max_page_index():
    # TODO(zj) parse the html to get the page total count
    max_index = 1
    list_question_url = "https://www.zhihu.com/topic/19550994/questions"
    resp = get_content(list_question_url)
    soup = BeautifulSoup(resp, "html.parser")
    soup.find('div', )
    pager = soup.find('div', attrs={'class': 'zm-invite-pager'})
    # <a href="?page=2">2</a>

    # print "............tag_a's parent:%s" % pager.find_all('a')
    for tag_a in pager.find_all('a'):
        # print ".........tag_a:%s" % tag_a
        page_number = int(tag_a.get('href').split('=')[1])
        # print "\n\n.........page number:%s" % page_number
        if page_number > max_index:
            max_index = page_number
    return int(max_index)

def generate_question_list_per_page(resp):
    # TODO(zj) parse the response
    return []