#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

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

from zhihu_util import *


LIST_QUESITON_PAGE_COUNT_PERCENTAGE = 1
QUESTION_WRITE_BUFFER_PAGE_COUNT = 10

def get_question_list_url(level2_topic_id, page_index):
    return "https://www.zhihu.com/topic/%s/questions?page=%s" % (level2_topic_id, page_index)


def write_question(temp_question_list, level2_topic_id, question_dir):
    if len(temp_question_list) == 0:
        return

    file_name = "%s/%s_question.data" % (question_dir, level2_topic_id)
    target = open(file_name, 'w+')
    for question_tuple in temp_question_list:
        question_list = list(question_tuple)
        question_str = ZHIHU_QUESTION_DATA_DELIMETER.join(map(str, question_list))
        target.write(question_str)
        target.write('\n')
    target.close()

def fetch_question_list_per_topic(level2_topic_id, run_mode='prod'):
    temp_question_list = []
    question_dir = get_question_data_directory()

    # URL-https://www.zhihu.com/topic/19552397/questions?page=1
    list_question_url = get_question_list_url(level2_topic_id, 1)
    max_page_index = get_max_page_index(list_question_url)

    print "\n......max page index:%s" % max_page_index
    page_index = 1
    while page_index <= get_page_index_threshold(max_page_index, run_mode):
        print "......topic %s, page_index: %s, page_total: %s" % \
              (level2_topic_id, page_index, max_page_index)
        list_question_url = get_question_list_url(level2_topic_id, page_index)
        resp = get_content(list_question_url)
        # print "......resp:%s" % resp
        question_list_per_page = generate_question_list_per_page(resp)
        temp_question_list += question_list_per_page
        if len(temp_question_list) > QUESTION_WRITE_BUFFER_PAGE_COUNT:
            write_question(temp_question_list, level2_topic_id, question_dir)
            temp_question_list = []
        page_index += 1
    write_question(temp_question_list, level2_topic_id, question_dir)


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
    time_arr = time.localtime(float(timestamp_ms)/1000)
    return time.strftime("%Y-%m-%d %H:%M:%S", time_arr)

def get_page_index_threshold(max_page_index, run_mode):
    if run_mode == "develop":
        return 1
    return int(ceil(LIST_QUESITON_PAGE_COUNT_PERCENTAGE * max_page_index))
