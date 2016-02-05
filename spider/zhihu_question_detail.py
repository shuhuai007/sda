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
import random

from zhihu_util import *
from zhihu_object import ZhihuObject
import zhihu_question_detail_parser

MAX_TOPIC_TABLE_ID = 15000
TOPIC_ID_STEP = 10

def generate_available_topic_ids():
    id_list = []
    # find the seed from config.ini
    topic_id_seed = get_topic_id_seed(get_local_ip())
    print "...............topic_id_seed:%s" % topic_id_seed
    # generate topic id each 10 steps. For example: 1, 11, 21, 31, 41, 51, ...
    topic_id = int(topic_id_seed)
    while topic_id < MAX_TOPIC_TABLE_ID:
        id_list.append(str(topic_id))
        topic_id += TOPIC_ID_STEP

    return ",".join(id_list)


def get_question_id_list():
    sample_file = "question_id.sample"
    file_object = open(sample_file, 'r')
    try:
        line = file_object.readline()
        question_id_list = line.split(",")
    finally:
        file_object.close()
    return question_id_list


class ZhihuQuestionDetail(ZhihuObject):
    def __init__(self, run_mode='prod'):
        ZhihuObject.__init__(self, run_mode)
        self.question_detail_thread_amount = int(self.cf.get("question_detail_thread_amount",
                                                             "question_detail_thread_amount"))

    def update_question(self):
        # 1. Get all the question id needed
        print "\n...Get all the question id needed"
        question_id_list = self.generate_question_id_list()
        print "\n...question_id_list's len:%s" % len(question_id_list)

        # 2. Resolve all the question id concurrently, save to local files
        self.fetch_question_detail(question_id_list)

    def generate_question_id_list(self):
        if self.is_develop_mode():
            return get_question_id_list()
        # TODO (zj) : need to get all the question id from db or file
        return []

    def fetch_question_detail(self, question_total_id_list):
        split_count = self.question_detail_thread_amount
        wm = WorkerManager(split_count)
        max_id = len(question_total_id_list)

        # print "...question_id_list:%s" % question_total_id_list

        for index in range(split_count):
            id_list = generate_id_list(int(index), split_count, max_id - 1)
            # print "...id_list:%s" % id_list
            question_id_list = map(lambda i: question_total_id_list[int(i)], id_list)
            wm.add_job(zhihu_question_detail_parser.update_question_detail, question_id_list)

        wm.wait_for_complete()


def main():
    mode, last_visit_date = parse_options()

    question_detail = ZhihuQuestionDetail(mode)
    print "question detail's mode:%s" % question_detail.mode

    question_detail.update_question()

if __name__ == '__main__':
    main()
