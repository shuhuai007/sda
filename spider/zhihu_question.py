#! /usr/bin/env python
# -*- coding: utf-8 -*-

from zhihu_util import *
from zhihu_object import ZhihuObject
import zhihu_question_parser

MAX_TOPIC_TABLE_ID = 15000
TOPIC_ID_STEP = 10


def generate_available_topic_ids(max_id=MAX_TOPIC_TABLE_ID, step=TOPIC_ID_STEP):
    id_list = []
    # find the seed from config.ini
    topic_id_seed = get_topic_id_seed(get_local_ip())
    print "...............topic_id_seed:%s" % topic_id_seed
    # generate topic id each 10 steps. For example: 1, 11, 21, 31, 41, 51, ...
    topic_id = int(topic_id_seed)
    while topic_id <= max_id:
        id_list.append(str(topic_id))
        topic_id += step

    return ",".join(id_list)


class ZhihuQuestion(ZhihuObject):
    def __init__(self, run_mode='prod'):
        ZhihuObject.__init__(self, run_mode)
        self.question_thread_amount = int(self.cf.get("question_thread_amount",
                                                      "question_thread_amount"))

    def update_question(self, last_visit_date):
        # Get the level 2 topic id list from db.
        print "\n...Get all the level2 topic info needed from db"
        level2_topic_id_list = self.get_level2_topic_id_list(last_visit_date)
        print "\n...level2_topic_id_list's len:%s" % len(level2_topic_id_list)
        # print "\n...level2_topic_id_list:%s" % level2_topic_id_list
        # exit()

        # Iterate each topic to find out all the questions
        wm = WorkerManager(self.question_thread_amount)
        index = 0
        for level2_topic_id in level2_topic_id_list:
            if self.is_develop_mode():
                if index >= 2:
                    break
            index += 1
            wm.add_job(self.update_question_for_each_topic, level2_topic_id)
        wm.wait_for_complete()

    def update_question_for_each_topic(self, level2_topic_id):
        print "\n...Begin, to fetch questions for topic - %s" % level2_topic_id
        zhihu_question_parser.fetch_question_list_per_topic(level2_topic_id, self.is_develop_mode())
        # self.persist_questions(question_list_per_topic)
        self.update_level2_topic_timestamp(level2_topic_id)

    def persist_questions(self, question_list_per_topic):
        insert_sql = "INSERT IGNORE INTO ZHIHU_QUESTION " \
                     "(QUESTION_ID, QUESTION_TITLE, ANSWER, IS_TOP_QUESTION, CREATED_TIME) " \
                     "VALUES (%s, %s, %s, %s, %s)"
        self.cursor.executemany(insert_sql, question_list_per_topic)

    def update_level2_topic_timestamp(self, level2_topic_id):
        sql = "UPDATE ZHIHU_TOPIC SET LAST_VISIT = %s WHERE TOPIC_ID = %s"
        self.cursor.execute(sql, (get_current_timestamp(), level2_topic_id))

    def get_level2_topic_id_list(self, last_visit_date):
        level2_topic_id_list = []
        sql = "SELECT TOPIC_ID FROM ZHIHU_TOPIC WHERE TOPIC_ID != PARENT_ID AND LAST_VISIT < '%s'" \
              % last_visit_date
        available_topic_ids = generate_available_topic_ids()
        sql += " AND ID IN (%s) " % available_topic_ids

        if self.is_develop_mode():
            sql += " LIMIT 2"

        print "......execute sql:%s" % sql

        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        for row in results:
            level2_topic_id_list.append(str(row[0]))

        return level2_topic_id_list


def main():
    run_mode, last_visit = parse_options()

    zhihu_question = ZhihuQuestion(run_mode)
    print "question's mode:%s" % zhihu_question.mode
    zhihu_question.update_question(last_visit)


if __name__ == '__main__':
    main()
