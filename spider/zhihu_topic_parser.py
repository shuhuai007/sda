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


LEVER2_TOPIC_COUNT_PER_PAGE = 20
LEVEL2_TOPIC_MAX_PAGE_INDEX = 1000


def fetch_level1_topic_dict(level1_topic_url=LEVEL1_TOPICS_URL):
    content = get_content(level1_topic_url)
    # print "...Level 1 topics's page content:%s" % content
    soup = BeautifulSoup(content, "html.parser")
    level1_ul = soup.find('ul', attrs={'class': 'zm-topic-cat-main clearfix'})
    # print "------level1_ul_tag:%s" % level1_ul
    level1_li_list = level1_ul.findAll('li')
    # print "------level1_li_list:%s" % level1_li_list

    # find hash_id,which will be used when sending request to fetch level2 topic
    #'<div class="zh-general-list clearfix" data-init="{&quot;params&quot;: {
    # &quot;topic_id&quot;: 253, &quot;offset&quot;: 0, &quot;hash_id&quot;: &quot;dced108689287057f5cc3b5e85cb8289&quot;}, &quot;nodename&quot;: &quot;TopicsPlazzaListV2&quot;}">'
    data_init_str = soup.find('div', attrs={'class': 'zh-general-list clearfix'}).get('data-init')
    data_init_json = json.loads(data_init_str)
    hash_id = data_init_json['params']['hash_id']

    level1_topic_list = []
    for level1_li in level1_li_list:
        topic_id = level1_li.get('data-id')
        topic_name = level1_li.a.get_text()
        # print "------topic_id:%s" % topic_id
        # print "------topic_name:%s" % topic_name
        level1_topic_list = level1_topic_list + [(topic_id, topic_name, topic_id)]
    level1_topic_dict = {"topic_list" : level1_topic_list, "hash_id" : hash_id}
    return level1_topic_dict

def fetch_level2_topic_list(level1_list, hash_id):
    level2_topic_list = []
    page_count = 0
    for (level1_topic_id, level1_topic_name, level1_parent_id) in level1_list:
        topic_url = generate_level2_topic_url()

        page_index = 1
        while page_index < LEVEL2_TOPIC_MAX_PAGE_INDEX:
            offset = (page_index - 1) * LEVER2_TOPIC_COUNT_PER_PAGE
            content = post(topic_url, generate_post_data_for_level2(hash_id, level1_topic_id, offset))
            # print "...level2 topic content:%s:" % content
            temp_list = parse_level2_response(content, level1_topic_id)
            if temp_list:
                level2_topic_list += temp_list
            if len(temp_list) < LEVER2_TOPIC_COUNT_PER_PAGE:
                # last page, break the loop
                break
            page_index += 1
        page_count += page_index

    print "...Total pagecount:%d" % page_count
    return level2_topic_list

def generate_level2_topic_url():
    return LEVEL2_TOPICS_URL

def parse_level2_response(content, level1_topic_id):
    '''
    :param content: is json str, just like: {"r":0, "msg": []}
    :return: list[(level2_topic_id, level2_topic_name)]
    '''
    decodejson = json.loads(content)
    # print "\n\n\n... decodejson's msg:%s" % decodejson['msg']

    '''
    <div class="item"><div class="blk">
        <a href="/topic/19564906" target="_blank">
            <img alt="Android 游戏" src="https://pic2.zhimg.com/35acee23dc6b42ee9abead8f2d00c9a5_xs.jpg">
            <strong>Android 游戏</strong>
            </img>
        </a>
        <p></p>
        <a class="follow meta-item zg-follow" href="javascript:;" id="t::-4897"><i class="z-icon-follow"></i>关注</a>
    </div></div>

    '''
    result_list = []
    for level2_div in decodejson['msg']:
        soup = BeautifulSoup(level2_div, "html.parser")
        # print "\n\n...soup:%s" % soup
        level2_topic_id = soup.find('a', attrs={'target': '_blank'}).get('href').split('/')[2]
        level2_topic_name = soup.find('strong').get_text()
        # print "\n\n...level2_topic_id:%s" % level2_topic_id
        # print "...level2_topic_name:%s" % level2_topic_name
        result_list.append((level2_topic_id, level2_topic_name, level1_topic_id))
    if len(result_list) < LEVER2_TOPIC_COUNT_PER_PAGE:
        print "\n\nresult_list's len:%d" % len(result_list)
    return result_list

def generate_post_data_for_level2(hash_id, level1_topic_id, offset):
    post_dict = {}
    post_dict["method"] = "next"
    # post_dict["params"] = '{"topic_id":253,"offset":40,"hash_id":"dced108689287057f5cc3b5e85cb8289"}'
    params_dict = '{' \
                  '"topic_id":' + str(level1_topic_id) + ',' \
                  '"offset":' + str(offset) + ',' \
                  '"hash_id":' + '"' + str(hash_id) + '"' \
                  '}'
    post_dict["params"] = params_dict
    print "\n\nparams_dict:%s" % params_dict
    # post_dict["_xsrf"] = "dacc17fefe1dd92f1f814fb77d3a359f"
    post_dict["_xsrf"] = get_xsrf()
    # print "\n\n...xsrf:%s" % post_dict["_xsrf"]
    post_data = urlencode(post_dict)
    # post_data = 'method=next&params=%7B%22topic_id%22%3A253%2C%22offset%22%3A40%2C%22hash_id%22%3A%22dced108689287057f5cc3b5e85cb8289%22%7D&_xsrf=dacc17fefe1dd92f1f814fb77d3a359f'
    return post_data
