#! /usr/bin/env python
# -*- coding: utf-8 -*-

import zhihu_topic_parser
import zhihu_util
from zhihu_item import ZhihuItem
from transaction_manager import TransactionManager


class ZhihuTopic(ZhihuItem):
    def __init__(self, run_mode='prod'):
        ZhihuItem.__init__(self, run_mode)
        self.topic_thread_amount = zhihu_util.get_thread_amount("topic_thread_amount")

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
        insert_sql = "INSERT IGNORE INTO ZHIHU_TOPIC (TOPIC_ID, NAME, PARENT_ID) " \
                     "VALUES (%s, %s, %s)"
        print "insert sql:%s" % insert_sql
        tm = TransactionManager()
        tm.execute_many_sql(insert_sql, topic_list)
        tm.close_connection()

def main():
    mode, last_visit_date = zhihu_util.parse_options()

    topic_util = ZhihuTopic(mode)
    print "topic's mode:%s" % topic_util.mode

    topic_util.update_topic()

if __name__ == '__main__':
    main()

