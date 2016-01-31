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
import zhihu_question_parser

class ZhihuQuestion(ZhihuObject):
    def __init__(self, run_mode='prod'):
        ZhihuObject.__init__(self, run_mode)
        self.question_thread_amount = int(self.cf.get("question_thread_amount",
                                                  "question_thread_amount"))

    def run(self):
        time_now = int(time.time())
        before_last_vist_time = time_now - 10

        queue = Queue.Queue()
        threads = []

        sql = "SELECT LINK_ID FROM TOPIC WHERE LAST_VISIT < %s ORDER BY LAST_VISIT"
        if self.is_develop_mode():
            sql += " LIMIT 2"

        print "---execute sql:%s"%sql
        # sys.exit(2)

        self.cursor.execute(sql, (before_last_vist_time,))
        results = self.cursor.fetchall()

        i = 0
        for row in results:
            link_id = str(row[0])

            queue.put([link_id, i])
            i = i + 1

        for i in range(self.topic_thread_amount):
            threads.append(UpdateOneTopic(queue))

        for i in range(self.topic_thread_amount):
            threads[i].start()

        for i in range(self.topic_thread_amount):
            threads[i].join()

        self.db.close()

        print 'All task done'

    def update_question_tmp(self):
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
        level2_list = list(set(level2_list))
        print "after distinct, level2_list's len:%d" % len(level2_list)

        # Persist topics into database
        print "persist topics into database"
        self.persist_topics(level1_list + level2_list)

    def update_question(self):
        # Get the level 2 topic id list from db.
        print "\n...Get all the topic info needed from db"
        level2_topic_id_list = self.get_level2_topic_id_list()
        print "\n...level2_topic_id_list's len:%s" % len(level2_topic_id_list)
        print "\n...level2_topic_id_list:%s" % level2_topic_id_list

        # Iterate each topic to find out all the questions
        question_list = zhihu_question_parser.fetch_question_list(level2_topic_id_list)

        # persisit question into database
        print "\n...Persist questions into db"
        self.persist_questions(question_list)

    def get_level2_topic_id_list(self):
        level2_topic_id_list = []
        sql = "SELECT TOPIC_ID FROM ZHIHU_TOPIC WHERE TOPIC_ID != PARENT_ID"
        if self.is_develop_mode():
            sql += " LIMIT 2"

        print "......execute sql:%s"%sql
        # sys.exit(2)

        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        for row in results:
            link_id = str(row[0])
            level2_topic_id_list.append(str(row[0]))

        return level2_topic_id_list

    def persist_questions(self, question_list):
        # TODO(zj) add logic
        return


def main():
    mode = zhihu_util.parse_options()

    zhihu_question = ZhihuQuestion(mode)
    print "question's mode:%s" % zhihu_question.mode

    zhihu_question.update_question()

if __name__ == '__main__':
    main()

