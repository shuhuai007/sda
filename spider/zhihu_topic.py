#! /usr/bin/env python
# -*- coding: utf-8 -*-


import json
from bs4 import BeautifulSoup
from urllib import urlencode

import zhihu_util
from zhihu_item import ZhihuItem
from zhihu_constants import *
from transaction_manager import TransactionManager


LEVER2_TOPIC_COUNT_PER_PAGE = 20
LEVEL2_TOPIC_MAX_PAGE_INDEX = 1000


class ZhihuTopic(ZhihuItem):
    def __init__(self, run_mode='prod'):
        ZhihuItem.__init__(self, run_mode)
        self.topic_thread_amount = zhihu_util.get_thread_amount("topic_thread_amount")

def update_topic():
    # Fetch 1st level topics
    print "Fetch 1st level topics from Zhihu ......"
    level1_dict = fetch_level1_topic_dict()
    level1_list = level1_dict["topic_list"]
    hash_id = level1_dict["hash_id"]

    print "level1_list's len:%d" % len(level1_list)
    print "level1_list's :%s" % level1_list

    # Fetch 2st level topics
    print "Fetch 2st level topics from Zhihu ......"
    level2_list = fetch_level2_topic_list(level1_list, hash_id)

    print "level1_list's len:%d" % len(level1_list)
    print "level2_list's len:%d" % len(level2_list)

    # Persist topics into database
    print "persist topics into database"
    persist_topics(level1_list + level2_list)

def fetch_level1_topic_dict(level1_topic_url=LEVEL1_TOPICS_URL):
    content = zhihu_util.get_content(level1_topic_url)
    # print "...Level 1 topics's page content:%s" % content
    soup = BeautifulSoup(content, "html.parser")
    level1_ul = soup.find('ul', attrs={'class': 'zm-topic-cat-main clearfix'})
    # print "------level1_ul_tag:%s" % level1_ul
    level1_li_list = level1_ul.findAll('li')
    # print "------level1_li_list:%s" % level1_li_list

    # find hash_id,which will be used when sending request to fetch level2 topic
    data_init_str = soup.find('div', attrs={'class': 'zh-general-list clearfix'}).get('data-init')
    data_init_json = json.loads(data_init_str)
    hash_id = data_init_json['params']['hash_id']

    level1_topic_list = []
    for level1_li in level1_li_list:
        topic_id = level1_li.get('data-id')
        topic_name = level1_li.a.get_text()
        # print "------topic_id:%s" % topic_id
        # print "------topic_name:%s" % topic_name
        level1_topic_list = level1_topic_list + [(topic_id, topic_name, topic_id)]
    level1_topic_dict = {"topic_list": level1_topic_list, "hash_id": hash_id}
    return level1_topic_dict

def fetch_level2_topic_list(level1_list, hash_id):
    level2_topic_list = []
    page_count = 0
    for (level1_topic_id, level1_topic_name, level1_parent_id) in level1_list:
        topic_url = generate_level2_topic_url()

        page_index = 1
        while page_index < LEVEL2_TOPIC_MAX_PAGE_INDEX:
            offset = (page_index - 1) * LEVER2_TOPIC_COUNT_PER_PAGE
            content = zhihu_util.post(topic_url,
                                      generate_post_data(hash_id, level1_topic_id, offset))
            # print "...level2 topic content:%s:" % content
            temp_list = parse_level2_response(content, level1_topic_id)
            if temp_list:
                level2_topic_list += temp_list
            if len(temp_list) < LEVER2_TOPIC_COUNT_PER_PAGE:
                # last page, break the loop
                break
            page_index += 1
        page_count += page_index

    print "\n\n...Total pagecount:%d" % page_count
    return level2_topic_list

def generate_level2_topic_url():
    return LEVEL2_TOPICS_URL

def parse_level2_response(content, level1_topic_id):
    """
    :param content: is json str, just like: {"r":0, "msg": []}
    :return: list[(level2_topic_id, level2_topic_name)]
    """
    decoded_json = json.loads(content)
    result_list = []
    for level2_div in decoded_json['msg']:
        soup = BeautifulSoup(level2_div, "html.parser")
        # print "\n\n...soup:%s" % soup
        level2_topic_id = soup.find('a', attrs={'target': '_blank'}).get('href').split('/')[2]
        level2_topic_name = soup.find('strong').get_text()
        # print "\n\n...level2_topic_id:%s" % level2_topic_id
        # print "...level2_topic_name:%s" % level2_topic_name
        result_list.append((level2_topic_id, level2_topic_name, level1_topic_id))
    if len(result_list) < LEVER2_TOPIC_COUNT_PER_PAGE:
        print "...result_list's len:%d" % len(result_list)
    return result_list

def generate_post_data(hash_id, level1_topic_id, offset):
    post_dict = {}
    try:
        post_dict["method"] = "next"
        params_dict = '{' \
                      '"topic_id":' + str(level1_topic_id) + ',' \
                      '"offset":' + str(offset) + ',' \
                      '"hash_id":' + '"' + str(hash_id) + '"' \
                      '}'
        post_dict["params"] = params_dict
        print "params_dict:%s" % params_dict
        # post_dict["_xsrf"] = "dacc17fefe1dd92f1f814fb77d3a359f"
        post_dict["_xsrf"] = zhihu_util.get_xsrf()
        # print "\n\n...xsrf:%s" % post_dict["_xsrf"]
        post_data = urlencode(post_dict)
    except:
        print "......Error in generate_post_data"
    return post_data

def persist_topics(topic_list):
    """
    Persist topics into mysql
    :param topic_list: all the topics including level 1 and level 2.
    :return: None
    """
    insert_sql = "INSERT IGNORE INTO ZHIHU_TOPIC (TOPIC_ID, NAME, PARENT_ID) \
                  VALUES (%s, %s, %s)"
    print "insert sql:%s" % insert_sql
    tm = TransactionManager()
    tm.execute_many_sql(insert_sql, topic_list)
    tm.close_connection()

def main():
    mode, last_visit_date = zhihu_util.parse_options()

    topic_util = ZhihuTopic(mode)
    print "topic's mode:%s" % topic_util.mode

    update_topic()


if __name__ == '__main__':
    main()
