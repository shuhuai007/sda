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

from zhihu_util import get_content
from zhihu_util import post

# 1st Level Topics url
LEVEL1_TOPICS_URL = "https://www.zhihu.com/topics"
LEVER2_PAGE_OFFSET = 20

def fetch_level1_topic_list(level1_topic_url=LEVEL1_TOPICS_URL):
    content = get_content(level1_topic_url)
    # print "...Level 1 topics's page content:%s" % content
    soup = BeautifulSoup(content, "html.parser")
    level1_ul = soup.find('ul', attrs={'class': 'zm-topic-cat-main clearfix'})
    # print "------level1_ul_tag:%s" % level1_ul
    level1_li_list = level1_ul.findAll('li')
    # print "------level1_li_list:%s" % level1_li_list
    level1_topic_list = []
    for level1_li in level1_li_list:
        topic_id = level1_li.get('data-id')
        topic_name = level1_li.a.get_text()
        # print "------topic_id:%s" % topic_id
        # print "------topic_name:%s" % topic_name
        level1_topic_list = level1_topic_list + [(topic_id, topic_name)]
    return level1_topic_list

def fetch_level2_topic_list(level1_list):
    offset = 0
    level2_topic_list = []
    for (level1_topic_id, level1_topic_name) in level1_list:
        topic_url = generate_level2_topic_url(level1_topic_id)
        content = post(topic_url, offset)
        print "...level2 topic content:%s:" % content

        temp_list = parse_level2_response(content)
        level2_topic_list += temp_list
        offset += LEVER2_PAGE_OFFSET
        break


def generate_level2_topic_url(level1_topic_id):
    return "https://www.zhihu.com/node/TopicsPlazzaListV2"

def parse_level2_response(content):
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
        print "\n\n...level2_topic_id:%s" % level2_topic_id
        print "...level2_topic_name:%s" % level2_topic_name
        result_list.append((level2_topic_id, level2_topic_name))
    print "\n\nresult_list's len:%d" % len(result_list)
    return result_list


