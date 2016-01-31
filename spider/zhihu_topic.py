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

class ZhihuTopicUtil:
    def __init__(self, run_mode='prod'):
        cf = ConfigParser.ConfigParser()
        cf.read("config.ini")
        
        host = cf.get("db", "host")
        port = int(cf.get("db", "port"))
        user = cf.get("db", "user")
        passwd = cf.get("db", "passwd")
        db_name = cf.get("db", "db")
        charset = cf.get("db", "charset")
        use_unicode = cf.get("db", "use_unicode")

        self.topic_thread_amount = int(cf.get("topic_thread_amount","topic_thread_amount"))

        self.db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db_name, charset=charset, use_unicode=use_unicode)
        self.cursor = self.db.cursor()
        self.mode = run_mode

    def is_develop_mode(self):
        return self.mode == 'develop'

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

        # Persist topics into database
        print "persist topics into database"
        self.persist_topics(level1_list + level2_list)

    def persist_topics(self, topic_list):
        # p_str = '  INSERT IGNORE INTO QUESTION (NAME, LINK_ID, FOCUS, ANSWER, LAST_VISIT, ADD_TIME, TOP_ANSWER_NUMBER) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        insert_sql = "INSERT IGNORE INTO ZHIHU_TOPIC (TOPIC_ID, NAME, PARENT_ID) VALUES (%s, %s, " \
                     "%s)"
        self.cursor.executemany(insert_sql,topic_list)

def usage():
    print 'topic.py usage:'
    print '-h,--help: print help message.'
    print '-m, --mode: develop or prod, prod is default value if not set.'

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hm:', ['mode='])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    mode = "prod"
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(1)
        elif opt in ('-m', '--mode'):
            mode = val
        else:
            print 'unhandled option'
            sys.exit(2)

    topic_util = ZhihuTopicUtil(mode)
    print "topic's mode:%s" % topic_util.mode

    topic_util.update_topic()

if __name__ == '__main__':
    main()

