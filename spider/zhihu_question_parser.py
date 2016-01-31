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
from zhihu_util import error_2_file


LIST_QUESITON_PAGE_COUNT_PERCENTAGE = 0.01

def get_question_list_url(level2_topic_id, page_index):
    return "https://www.zhihu.com/topic/%s/questions?page=%s" % (level2_topic_id, page_index)


def fetch_question_list_per_topic(level2_topic_id):
    temp_question_list = []

    # URL-https://www.zhihu.com/topic/19552397/questions?page=1
    list_question_url = get_question_list_url(level2_topic_id, 1)
    max_page_index = get_max_page_index(list_question_url)

    print "\n......max page index:%s" % max_page_index
    page_index = 1
    while page_index <= int(round(LIST_QUESITON_PAGE_COUNT_PERCENTAGE * max_page_index)):
        # print "......enter while loop"
        list_question_url = get_question_list_url(level2_topic_id, page_index)
        resp = get_content(list_question_url)
        # print "......resp:%s" % resp
        question_list_per_page = generate_question_list_per_page(resp)
        temp_question_list += question_list_per_page
        page_index += 1
    return temp_question_list

def get_max_page_index(list_question_url):
    max_index = 1
    try:
        resp = get_content(list_question_url)
        soup = BeautifulSoup(resp, "html.parser")
        pager = soup.find('div', attrs={'class': 'zm-invite-pager'})
        # <a href="?page=2">2</a>

        # print "............tag_a's parent:%s" % pager.find_all('a')
        for tag_a in pager.find_all('a'):
            # print ".........tag_a:%s" % tag_a
            page_number = int(tag_a.get('href').split('=')[1])
            # print "\n\n.........page number:%s" % page_number
            if page_number > max_index:
                max_index = page_number
    except:
        print "Fail to get max_index when parsing html"
        error_2_file("\n------------------\n" + str(soup) + "------------------",
                     'question_error.log')

    return int(max_index)

def generate_question_list_per_page(resp):
    question_list = []
    soup = BeautifulSoup(resp, "html.parser")
    div_tag_list = soup.find_all('div', attrs={'class' : 'feed-item feed-item-hook question-item'})

    for div_tag in div_tag_list:
        try:
            # print ".........div_tag:%s" % div_tag
            answer_count = div_tag.find('meta', attrs={'itemprop' : 'answerCount'}).get('content')
            is_top_quesiton = div_tag.find('meta', attrs={'itemprop' : 'isTopQuestion'}).get('content')
            # print "...............is_top_quesiton:%s" % is_top_quesiton
            if is_top_quesiton == 'true':
                is_top_quesiton = 1
            else:
                is_top_quesiton = 0

            h2_tag = div_tag.find('h2', attrs={'class', 'question-item-title'})
            question_title = h2_tag.a.get_text()
            question_id = h2_tag.a.get('href').split('/')[2]
            timestamp_ms = h2_tag.span.get('data-timestamp')
            created_time = transfer_timestamp(timestamp_ms)
            question_list.append((question_id, question_title, answer_count, is_top_quesiton, created_time))
        except:
            print "Fail to parse when executing generate_question_list_per_page()... "

    return question_list


def transfer_timestamp(timestamp_ms):
    timeArray = time.localtime(float(timestamp_ms)/1000)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime