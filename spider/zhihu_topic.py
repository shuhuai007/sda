#! /usr/bin/env python
# -*- coding: utf-8 -*-


import json
from bs4 import BeautifulSoup
from urllib import urlencode

import zhihu_util
from zhihu_constants import *
from transaction_manager import TransactionManager


LEVER2_TOPIC_COUNT_PER_PAGE = 20
LEVEL2_TOPIC_MAX_PAGE_INDEX = 1000


class ZhihuTopicSquare:

    def __init__(self, square_url, run_mode='prod'):
        self.square_url = square_url
        self.run_mode = run_mode
        content = zhihu_util.get_content(self.square_url)
        # print "...Level 1 topics's page content:%s" % content
        self._soup = BeautifulSoup(content, "html.parser")

    def _get_hash_id(self):
        data_init_str = self._soup.find('div', attrs={'class': 'zh-general-list clearfix'}) \
                            .get('data-init')
        data_init_json = json.loads(data_init_str)
        hash_id = data_init_json['params']['hash_id']
        return hash_id

    def get_level1_topics(self):

        level1_li_list = self._soup.find('ul', attrs={'class': 'zm-topic-cat-main clearfix'})\
                                   .findAll('li')

        # find hash_id,which will be used when sending request to fetch level2 topic
        hash_id = self._get_hash_id()

        for level1_li in level1_li_list:
            topic_id = level1_li.get('data-id')
            topic_name = level1_li.a.get_text()
            level1_topic = ZhihuLevel1Topic(topic_id, topic_name, topic_id, hash_id)
            yield level1_topic

    def get_level2_topics(self):
        result_list = []
        for level1_topic in self.get_level1_topics():
            result_list += level1_topic.get_level2_topics()
        return result_list

    def get_all_topics(self):
        return list(self.get_level1_topics()) + self.get_level2_topics()


class ZhihuTopic:

    def __init__(self, topic_id, topic_name, parent_id, run_mode='prod'):
        # ZhihuItem.__init__(self, run_mode)
        self.topic_id = topic_id
        self.topic_name = topic_name
        self.parent_id = parent_id
        self.topic_thread_amount = zhihu_util.get_thread_amount("topic_thread_amount")

    def get_parent_id(self):
        return self.parent_id

    def get_topic_id(self):
        return self.topic_id

    def get_topic_name(self):
        return self.topic_name

    def get_fields(self):
        return self.topic_id, self.topic_name, self.parent_id


class ZhihuLevel1Topic(ZhihuTopic):

    def __init__(self, topic_id, topic_name, parent_id, hash_id, post_url=LEVEL2_TOPICS_URL,
                 run_mode='prod'):
        ZhihuTopic.__init__(self, topic_id, topic_name, parent_id)
        self.post_url = post_url
        self.hash_id = hash_id

    def get_level2_topics(self):
        level2_topic_list = []
        page_count = 0
        level2_url = self.post_url

        page_index = 1
        while page_index < LEVEL2_TOPIC_MAX_PAGE_INDEX:
            offset = (page_index - 1) * LEVER2_TOPIC_COUNT_PER_PAGE
            content = zhihu_util.post(level2_url,
                                      generate_post_data(self.hash_id, self.topic_id, offset))
            decoded_json = json.loads(content)
            temp_list = []
            for level2_div in decoded_json['msg']:
                soup = BeautifulSoup(level2_div, "html.parser")
                level2_topic_id = soup.find('a', attrs={'target': '_blank'}).get('href').split('/')[2]
                level2_topic_name = soup.find('strong').get_text()
                temp_list.append(ZhihuLevel2Topic(level2_topic_id, level2_topic_name, self.parent_id))
            if temp_list:
                level2_topic_list += temp_list
            if len(temp_list) < LEVER2_TOPIC_COUNT_PER_PAGE:
                # last page, break the loop
                break
            page_index += 1
        page_count += page_index
        print "...Total pagecount:%d" % page_count
        return level2_topic_list


class ZhihuLevel2Topic(ZhihuTopic):
    def __init__(self, topic_id, topic_name, parent_id, run_mode='prod'):
        # ZhihuItem.__init__(self, run_mode)
        ZhihuTopic.__init__(self, topic_id, topic_name, parent_id)


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
    square_url = "https://www.zhihu.com/topics"
    topic_square = ZhihuTopicSquare(square_url, mode)
    print "topic's mode:%s" % topic_square.run_mode

    topics = topic_square.get_all_topics()
    print("topic total's size:{}".format(len(topics)))

    persist_topics(topics)


if __name__ == '__main__':
    main()
