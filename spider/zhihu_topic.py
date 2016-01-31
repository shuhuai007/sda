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

import zhihu_topic_parser
import zhihu_util
from zhihu_object import ZhihuObject

class ZhihuTopic(ZhihuObject):
    def __init__(self, run_mode='prod'):
        ZhihuObject.__init__(self, run_mode)
        self.topic_thread_amount = int(self.cf.get("topic_thread_amount",
                                                      "topic_thread_amount"))

    def update_topic(self):
        # Fetch 1st level topics
        print "\n\nFetch 1st level topics from Zhihu ......"
        level1_dict = zhihu_topic_parser.fetch_level1_topic_dict()
        level1_list = level1_dict["topic_list"]
        hash_id = level1_dict["hash_id"]

        print "level1_list's len:%d" % len(level1_list)
        print "level1_list's :%s" % level1_list

        # Fetch 2st level topics
        print "\n\nFetch 2st level topics from Zhihu ......"

        level2_list = zhihu_topic_parser.fetch_level2_topic_list(level1_list, hash_id)

        print "level1_list's len:%d" % len(level1_list)
        print "level2_list's len:%d" % len(level2_list)
        # level2_topic_id_list = map(lambda x: x[0], level2_list)
        # level2_topic_id_list = list(set(level2_topic_id_list))
        # print "after distinct, level2_topic_id_list's len:%d" % len(level2_topic_id_list)

        # Persist topics into database
        print "persist topics into database"
        self.persist_topics(level1_list + level2_list)

    def persist_topics(self, topic_list):
        # p_str = '  INSERT IGNORE INTO QUESTION (NAME, LINK_ID, FOCUS, ANSWER, LAST_VISIT, ADD_TIME, TOP_ANSWER_NUMBER) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        insert_sql = "INSERT IGNORE INTO ZHIHU_TOPIC (TOPIC_ID, NAME, PARENT_ID) VALUES (%s, %s, " \
                     "%s)"
        self.cursor.executemany(insert_sql,topic_list)

def main():
    mode = zhihu_util.parse_options()

    topic_util = ZhihuTopic(mode)
    print "topic's mode:%s" % topic_util.mode

    topic_util.update_topic()

if __name__ == '__main__':
    main()

