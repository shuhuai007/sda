#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import time

from bs4 import BeautifulSoup
from zhihu_constants import *

from zhihu_util import *

ZHIHU_QUESTION_DETAIL_URL = "https://www.zhihu.com/question/{0}"

# BUFFER SIZE is 10000 quesitons
QUESTION_WRITE_BUFFER_SIZE = 10000

def get_question_content(soup):
    content = ""
    try:
        content = soup.find('div', attrs={'id': 'zh-question-detail'}). \
            find('div', attrs={'class':'zm-editable-content'}).get_text()
    except:
        print "...get content error"
    return content


def get_comment_count(soup):
    count = 0
    try:
        comment = soup.find('div', attrs={'id': 'zh-question-meta-wrap'}). \
            find('a', attrs={'name': 'addcomment'}).get_text()
        # print "......comment:%s" % comment
        import re
        count = re.findall(r"\d+\.?\d*", comment)[0]
    except:
        print "......get comment count error, it will be 0"
    # print "......comment count:%s" % count
    return count

def get_focus_count(soup):
    count = 0
    try:
        count = soup.find('div', attrs={'id': 'zh-question-side-header-wrap'}). \
            find('div', attrs={'class': 'zg-gray-normal'}).a.strong.get_text()
        count = int(count)
    except:
        print "......get count error, it will be 0"
    print "......focus count:%s" % count

    return count


def get_focus_users(soup):
    user_list = []
    soup = soup.find('div', attrs={'id': 'zh-question-side-header-wrap'})
    a_tag = soup.find_all('a')
    for item in a_tag:
        # href="/people/jin-chen-ran-79"
        user_name = item.get('href').split("/")[2]
        if user_name.strip():
            user_list.append(user_name)
    print "......focus user list:%s" % ",".join(user_list)
    return ",".join(user_list)


def get_browse_count(soup):
    try:
        count = soup.find('meta', attrs={'itemprop': 'visitsCount'}).get('content')
    except:
        print "......get visitsCount error"
    print "......browse_count:%s" % count
    return count


def get_related_focus_info(soup):
    related_focus = 0
    last_edited = ""
    try:
        question_status_div = soup.find('h3', text="问题状态").parent
        last_edited = question_status_div.find('span', attrs={'class': 'time'}).get_text()
        related_focus = question_status_div.find_all('strong')[1].get_text()
    except:
        print "......get_related_focus_info error"
    print "......related_focus, last_edited : (%s,%s)" % (related_focus, last_edited)
    return related_focus, last_edited
    # print "......quesiton_status_div:%s" % quesiton_status_div


def update_question_detail(question_id_list):
    if not question_id_list:
        return

    buffer_list = []
    for question_id in question_id_list:
        # print "index:%s, question id:%s" % (index, question_id_list[int(index)])
        print "......question id:%s" % question_id
        request_url = ZHIHU_QUESTION_DETAIL_URL.format(question_id)
        resp = get_content(request_url)
        # print "......request_url's response:%s" % resp
        soup = BeautifulSoup(resp, "html.parser")
        question_content = get_question_content(soup)
        comment_count = get_comment_count(soup)
        focus = get_focus_count(soup)
        focus_user_list = get_focus_users(soup)
        browse_count = get_browse_count(soup)
        related_focus, last_edited = get_related_focus_info(soup)
        spider_time = get_current_timestamp()
        buffer_list.append((question_id, question_content, comment_count, focus, focus_user_list,
                            browse_count, related_focus, last_edited, spider_time))

        if len(buffer_list) >= QUESTION_WRITE_BUFFER_SIZE:
            write_buffer(buffer_list, question_id)
    write_buffer(buffer_list, question_id)
    print "...buffer_list:%s" % buffer_list


def write_buffer(buffer_list, question_id):
    dir_name = get_question_data_directory()
    buffer_filename = "%s/question-detail-%s-%s" % (dir_name, question_id, int(time.time()))
    # print "......buffer_filename:%s" % buffer_filename
    write_buffer_file(buffer_list, buffer_filename, "question-detail-delimiter")
