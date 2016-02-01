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

    def update_question(self):
        # Get the level 2 topic id list from db.
        print "\n...Get all the level2 topic info needed from db"
        level2_topic_id_list = self.get_level2_topic_id_list()
        print "\n...level2_topic_id_list's len:%s" % len(level2_topic_id_list)
        # print "\n...level2_topic_id_list:%s" % level2_topic_id_list

        # Iterate each topic to find out all the questions
        for level2_topic_id in level2_topic_id_list:
            print "\n...Begin, to fetch quesitons for topic - %s" % level2_topic_id
            question_list_per_topic = zhihu_question_parser.fetch_question_list_per_topic(level2_topic_id)
            print "\n...End, the topic %s has %s questions" % (level2_topic_id, len(question_list_per_topic))
            self.persist_questions(question_list_per_topic)
            self.update_level2_topic_timestamp(level2_topic_id)

    def persist_questions(self, question_list_per_topic):
        insert_sql = "INSERT IGNORE INTO ZHIHU_QUESTION (QUESTION_ID, QUESTION_TITLE, ANSWER, IS_TOP_QUESTION, CREATED_TIME) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.executemany(insert_sql, question_list_per_topic)

    def update_level2_topic_timestamp(self, level2_topic_id):
        sql = "UPDATE ZHIHU_TOPIC SET LAST_VISIT = %s WHERE TOPIC_ID = %s"
        self.cursor.execute(sql,(zhihu_util.get_current_timestamp(), level2_topic_id))

    def get_level2_topic_id_list(self):
        level2_topic_id_list = []
        today_date = zhihu_util.get_today_date()
        sql = "SELECT TOPIC_ID FROM ZHIHU_TOPIC WHERE TOPIC_ID != PARENT_ID AND LAST_VISIT < '%s'" % today_date

        if self.is_develop_mode():
            sql += " LIMIT 2"

        print "......execute sql:%s"%sql

        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        for row in results:
            level2_topic_id_list.append(str(row[0]))

        return level2_topic_id_list


def main():
    mode = zhihu_util.parse_options()

    zhihu_question = ZhihuQuestion(mode)
    print "question's mode:%s" % zhihu_question.mode

    zhihu_question.update_question()

if __name__ == '__main__':
    main()

