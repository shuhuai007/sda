#! /usr/bin/env python
# -*- coding: utf-8 -*-

from zhihu_util import *
from zhihu_item import ZhihuItem
import zhihu_question_detail_parser


MAX_QUESTION_TABLE_ID = 4000000
QUESTION_ID_STEP = 10
AVAIL_ID_SIZE_THRESHOLD = 10000


def get_question_id_list():
    import os
    sample_file = os.path.abspath((os.path.dirname(__file__)) + "/question_id.sample")
    question_id_list = []
    with open(sample_file, 'r') as f:
        question_id_list.append(f.readline().split(","))
    return question_id_list


class ZhihuQuestionDetail(ZhihuItem):

    def __init__(self, run_mode='prod'):
        ZhihuItem.__init__(self, run_mode)
        self.question_detail_thread_amount = get_question_detail_thread_amount()

    def is_develop_mode(self):
        return self.mode == 'develop'

    def update_question(self, last_visit):
        # 1. Get all the question id needed
        print "...Get all the question id needed"
        question_id_list = self.generate_question_id_list(last_visit)
        print "...question_id_list's len:%s" % len(question_id_list)

        # 2. Resolve all the question id concurrently, save to local files
        self.fetch_question_detail(question_id_list)

    def generate_question_id_list(self, last_visit):
        question_id_list = []
        if self.is_develop_mode():
            return get_question_id_list()

        available_ids = generate_available_topic_ids(MAX_QUESTION_TABLE_ID, QUESTION_ID_STEP)
        available_id_list = available_ids.split(',')

        # debug code
        # available_id_list = ['40079131', '26497360', '39977714', '39019297']

        import math
        loop = int(math.ceil(float(len(available_id_list))/AVAIL_ID_SIZE_THRESHOLD))
        print "......loop:%s" % loop
        i = 0
        pre_sql = None
        while i < loop:
            tm = self.transaction_manager
            begin_index = i * AVAIL_ID_SIZE_THRESHOLD
            end_index = (i + 1) * AVAIL_ID_SIZE_THRESHOLD

            sql = "SELECT QUESTION_ID " \
                  "FROM (select @index:=@index+1 as ID, QUESTION_ID, LAST_VISIT from ZHIHU_QUESTION_ID) AS q  " \
                  "WHERE timestamp(q.LAST_VISIT) < timestamp('%s')" % last_visit
            sql += " AND ID IN (%s) " % ",".join(available_id_list[begin_index:end_index])

            # print "...sql:%s" % sql
            if i == 1:
                pre_sql = "SET @index=0;"
            results = tm.execute_sql(sql, pre_sql)
            for row in results:
                question_id_list.append(str(row[0]))
            i += 1

        return question_id_list

    def fetch_question_detail(self, question_total_id_list):
        if len(question_total_id_list) == 0:
            return
        split_count = self.question_detail_thread_amount
        wm = WorkerManager(split_count)
        max_id = len(question_total_id_list)
        # print "...question_id_list:%s" % question_total_id_list
        print "...Thread count:%s" % split_count
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

    question_detail.update_question(last_visit_date)


if __name__ == "__main__":
    main()
