#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup
from zhihu_util import *


# BUFFER SIZE of questions
QUESTION_WRITE_BUFFER_SIZE = 10000


def get_question_content(soup):
    content = ""
    try:
        content = soup.find('div', attrs={'id': 'zh-question-detail'}). \
            find('div', attrs={'class': 'zm-editable-content'}).get_text()
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
    # print "......focus count:%s" % count

    return count

def get_focus_users(soup):
    user_list = []
    try:
        soup = soup.find('div', attrs={'id': 'zh-question-side-header-wrap'})
        a_tag = soup.find_all('a')
        for item in a_tag:
            # href="/people/jin-chen-ran-79"
            user_name = item.get('href').split("/")[2]
            if user_name.strip():
                user_list.append(user_name)
        # print "......focus user list:%s" % ",".join(user_list)
    except Exception,e:
        print "......Couldn't get user list, will be empty string"
    return ",".join(user_list)

def get_browse_count(soup):
    count = 0
    try:
        count = soup.find('meta', attrs={'itemprop': 'visitsCount'}).get('content')
    except:
        print "......get visitsCount error"
    # print "......browse_count:%s" % count
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
            write_buffer(buffer_list)
            buffer_list = []
    write_buffer(buffer_list)
    # print "...buffer_list:%s" % buffer_list

def write_buffer(buffer_list):
    if len(buffer_list) == 0:
        return
    dir_name = get_question_data_directory()
    buffer_filename = "%s/question-detail-%s-%s" % (dir_name, buffer_list[0][0], int(time.time()))
    # print "......buffer_filename:%s" % buffer_filename
    write_buffer_file(buffer_list, buffer_filename, ZHIHU_QUESTION_DETAIL_FIELD_DELIMITER)

    # update the question_id_list in db
    # update_buffer_to_db(buffer_list)

def update_buffer_to_db(buffer_list, tm):
    question_id_list = map(lambda question: question[0], buffer_list)
    sql = "UPDATE ZHIHU_QUESTION_ID SET LAST_VISIT = %s WHERE QUESTION_ID = %s"
    ts = get_current_timestamp()
    args = map(lambda question_id: (ts, question_id), question_id_list)
    print "......Update sql:%s, args:%s" % (sql, args)
    tm.execute_many_sql(sql, args)
