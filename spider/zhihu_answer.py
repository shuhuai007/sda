#! /usr/bin/env python
# -*- coding: utf-8 -*-

from zhihu_util import *
from zhihu_item import ZhihuItem
from transaction_manager import TransactionManager
import zhihu_answer_parser


MAX_QUESTION_TABLE_ID = 4000000
QUESTION_ID_STEP = 10
AVAIL_ID_SIZE_THRESHOLD = 10000


def generate_available_ids(max_id, step):
    id_list = []
    # find the seed from config.ini
    id_seed = get_topic_id_seed(get_local_ip())
    print "...............id_seed:%s" % id_seed
    # generate topic id each 10 steps. For example: 1, 11, 21, 31, 41, 51, ...
    id = int(id_seed)
    while id < max_id:
        id_list.append(str(id))
        id += step

    return ",".join(id_list)


def get_question_id_list():
    sample_file = QUESTION_ID_SAMPLE_PATH
    file_object = open(sample_file, 'r')
    try:
        line = file_object.readline()
        question_id_list = line.split(",")
    finally:
        file_object.close()
    return question_id_list


class ZhihuAnswer(ZhihuItem):

    def __init__(self, run_mode='prod'):
        ZhihuItem.__init__(self, run_mode)
        self.question_detail_thread_amount = get_question_detail_thread_amount()

    def is_develop_mode(self):
        return self.mode == 'develop'

    def update_answer(self, last_visit):
        # 1. Get all the question id needed
        print "\n...Get all the question id needed"
        question_id_list = self.generate_question_id_list(last_visit)
        print "\n...question_id_list's len:%s" % len(question_id_list)

        # 2. Resolve all the question id concurrently, save to local files
        self.fetch_answer(question_id_list)

    def generate_question_id_list(self, last_visit):
        question_id_list = []
        if self.is_develop_mode():
            return get_question_id_list()

        available_ids = generate_available_ids(MAX_QUESTION_TABLE_ID, QUESTION_ID_STEP)
        available_id_list = available_ids.split(',')

        # debug code
        # available_id_list = ['40079131', '26497360', '39977714', '39019297']

        import math
        loop = int(math.ceil(float(len(available_id_list))/AVAIL_ID_SIZE_THRESHOLD))
        print "......loop:%s" % loop
        i = 0
        pre_sql = None
        while i < loop:
            tm = TransactionManager()
            begin_index = i * AVAIL_ID_SIZE_THRESHOLD
            end_index = (i + 1) * AVAIL_ID_SIZE_THRESHOLD

            sql = "SELECT QUESTION_ID FROM (select @index:=@index+1 as ID, QUESTION_ID, LAST_VISIT from ZHIHU_QUESTION_ID) AS q  WHERE timestamp(q.LAST_VISIT) < timestamp('%s')"  % last_visit
            sql += " AND ID IN (%s) " % ",".join(available_id_list[begin_index:end_index])

            # print "...sql:%s" % sql
            if i == 1:
                pre_sql = "SET @index=0;"
            results = tm.execute_sql(sql, pre_sql)
            for row in results:
                question_id_list.append(str(row[0]))
            i += 1

        return question_id_list

    def fetch_answer(self, question_total_id_list):
        if len(question_total_id_list) == 0:
            return
        split_count = self.question_detail_thread_amount
        tm = TransactionManager()
        wm = WorkerManager(split_count)
        max_id = len(question_total_id_list)

        # print "...question_id_list:%s" % question_total_id_list
        print "...Thread count:%s" % split_count
        for index in range(split_count):
            id_list = generate_id_list(int(index), split_count, max_id - 1)
            print "...id_list:%s" % id_list
            question_id_list = map(lambda i: question_total_id_list[int(i)], id_list)
            print "...question_id_list:%s" % question_id_list
            wm.add_job(zhihu_answer_parser.update_answer, question_id_list, tm)

        wm.wait_for_complete()

def main():
    mode, last_visit_date = parse_options()

    answer = ZhihuAnswer(mode)
    print "zhihu answer's mode:%s" % answer.mode

    answer.update_answer(last_visit_date)

if __name__ == '__main__':
    main()
