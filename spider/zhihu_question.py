#! /usr/bin/env python
# -*- coding: utf-8 -*-


from zhihu_util import *
from zhihu_item import ZhihuItem
from transaction_manager import TransactionManager
import zhihu_question_parser

MAX_TOPIC_TABLE_ID = 15000
TOPIC_ID_STEP = 10


class ZhihuQuestion(ZhihuItem):

    def __init__(self, run_mode='prod'):
        ZhihuItem.__init__(self, run_mode)
        self.question_thread_amount = get_thread_amount("question_thread_amount")

    def update_question(self, last_visit_date):
        # Get the level 2 topic id list from db.
        print "...Get all the level2 topic info needed from db"
        level2_topic_id_list = get_level2_topic_id_list(last_visit_date, self.is_develop_mode())
        print "...level2_topic_id_list's len:%s" % len(level2_topic_id_list)
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
        update_level2_topic_timestamp(level2_topic_id)

    def persist_questions(self, question_list_per_topic):
        insert_sql = "INSERT IGNORE INTO ZHIHU_QUESTION " \
                     "(QUESTION_ID, QUESTION_TITLE, ANSWER, IS_TOP_QUESTION, CREATED_TIME) " \
                     "VALUES (%s, %s, %s, %s, %s)"
        tm = TransactionManager()
        tm.execute_many_sql(insert_sql, question_list_per_topic)
        tm.close_connection()


def update_level2_topic_timestamp(level2_topic_id):
    sql = "UPDATE ZHIHU_TOPIC SET LAST_VISIT = '%s' WHERE TOPIC_ID = %s" % \
          (get_current_timestamp(), level2_topic_id)
    tm = TransactionManager()
    tm.execute_sql(sql)
    tm.close_connection()

def get_level2_topic_id_list(last_visit_date, is_develop=False):
    level2_topic_id_list = []
    sql = "SELECT TOPIC_ID FROM ZHIHU_TOPIC WHERE TOPIC_ID != PARENT_ID AND LAST_VISIT < '%s'" \
          % last_visit_date
    available_topic_ids = generate_available_topic_ids(MAX_TOPIC_TABLE_ID, TOPIC_ID_STEP)
    sql += " AND ID IN (%s) " % available_topic_ids

    if is_develop:
        sql += " LIMIT 2"

    print "......execute sql:%s" % sql
    tm = TransactionManager()
    results = tm.execute_sql(sql)
    tm.close_connection()

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
