#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import json

from bs4 import BeautifulSoup
from zhihu_constants import *
from urllib import urlencode


from zhihu_util import *

# TODO (zj) need to generate answer's url

# BUFFER SIZE
ANSWER_BUFFER_SIZE = 100

ANSWER_MAX_PAGE_INDEX = 1000
ANSWER_COUNT_PER_PAGE = 20


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


def generate_post_data(question_id, offset, pagesize=20):
    # method:next
    # params:{"url_token":39295324,"pagesize":20,"offset":20}
    # _xsrf:81d4317bc49ba8e6a35c9a9da4c7c58f
    post_data = None
    post_dict = {}
    try:
        post_dict["method"] = "next"
        params_dict = '{' \
                      '"url_token":' + str(question_id) + ',' \
                      '"offset":' + str(offset) + ',' \
                      '"pagesize":' + '"' + str(pagesize) + '"' \
                      '}'
        post_dict["params"] = params_dict
        print "\n\nparams_dict:%s" % params_dict
        # post_dict["_xsrf"] = "dacc17fefe1dd92f1f814fb77d3a359f"
        post_dict["_xsrf"] = get_xsrf()
        # print "\n\n...xsrf:%s" % post_dict["_xsrf"]
        post_data = urlencode(post_dict)
    except Exception, e:
        print "...Error when generating postdata for list answers, error message:%s" % e.message

    return post_data


def get_answer_id(soup):
    answer_id = '0'
    try:
        answer_id = soup.find('div', attrs={'class': 'zm-item-answer zm-item-expanded'})\
                        .get("data-atoken")
    except:
        print "......get answer_id error, it will be 0"
    # print "......answer_id:%s" % answer_id
    return answer_id

def get_comment_count(soup):
    count = 0
    try:
        comment = soup.find('a', attrs={'name': 'addcomment'}).get_text()
        # print "......comment:%s" % comment
        import re
        count = re.findall(r"\d+\.?\d*", comment)[0]
    except:
        print "......get comment count error, it will be 0"
    # print "......comment count:%s" % count
    return count


def get_answer_content(soup):
    answer_content = ""
    try:
        answer_content = soup.find('div', attrs={'class': 'zm-editable-content clearfix'}) \
                             .get_text()
        answer_content = answer_content.strip()
    except:
        print "......get answer content error, it will be empty string"
    # print "......answer_content:%s" % answer_content
    return answer_content


def get_data_aid(soup):
    aid = '0'
    try:
        aid = soup.find('div', attrs={'class': 'zm-item-answer zm-item-expanded'}) \
                  .get("data-aid")
    except:
        print "......get data-aid error, it will be 0"
    # print "......answer data-aid:%s" % aid
    return aid


def get_username(soup):
    username = 'anonymous'
    try:
        username_link = soup.find('div', attrs={'class': 'answer-head'})\
                            .find('a', attrs={'class': 'author-link'})\
                            .get("href")
        # print "......usernmae_link:%s" % username_link
        username = username_link.split('/')[2]
    except:
        print "......get username error, it will be anonymous"
    # print "......answer username:%s" % username
    return username


def get_vote_count(soup):
    count = '0'
    try:
        count = soup.find('button', attrs={'class': 'up'})\
                    .find('span', attrs={'class': 'count'})\
                    .get_text()
    except:
        print "......get vote count error, it will be 0"
    # print "......vote count:%s" % count
    return count


def get_created_time(soup):
    created = '0'
    try:
        created = soup.find('div', attrs={'class': 'zm-item-answer zm-item-expanded'})\
                      .get("data-created")
    except:
        print "......get created time error, it will be 0"
    # print "......created time:%s" % created
    return created


def generate_answer_list(resp):
    result_list = []

    decoded_json = json.loads(resp)
    for item_div in decoded_json['msg']:
        soup = BeautifulSoup(item_div, "html.parser")

        answer_id = get_answer_id(soup)
        answer_content = get_answer_content(soup)
        data_aid = get_data_aid(soup)
        user_name = get_username(soup)
        created_time = get_created_time(soup)
        vote_count = get_vote_count(soup)
        comment_count = get_comment_count(soup)
        result_list.append((answer_id, answer_content, data_aid, user_name, created_time,
                            vote_count, comment_count))
    return result_list


def get_answers_for_question(question_id):
    request_url = ZHIHU_ANSWER_POST_URL

    buffer_list = []
    page_index = 1
    while page_index < ANSWER_MAX_PAGE_INDEX:
        offset = (page_index - 1) * ANSWER_COUNT_PER_PAGE
        post_data = generate_post_data(question_id, offset)
        resp = post(request_url, post_data)
        # print "...resp:%s" % resp
        answer_list = generate_answer_list(resp)
        buffer_list += answer_list

        if len(buffer_list) >= ANSWER_BUFFER_SIZE:
            write_buffer(buffer_list, question_id)
            buffer_list = []
        if len(answer_list) < ANSWER_COUNT_PER_PAGE:
            break
        page_index += 1
    write_buffer(buffer_list, question_id)
    print "...buffer_list's length:%s" % len(buffer_list)


def update_answer(question_id_list, tm):
    print "...enter update_answer..."
    if not question_id_list:
        return

    for question_id in question_id_list:
        # print "index:%s, question id:%s" % (index, question_id_list[int(index)])
        print "......question id:%s" % question_id
        get_answers_for_question(question_id)

def write_buffer(buffer_list, question_id):
    if len(buffer_list) == 0:
        return
    dir_name = get_question_data_directory()
    buffer_filename = "%s/answer-%s-%s" % (dir_name, question_id, int(time.time()))
    # print "......buffer_filename:%s" % buffer_filename
    write_buffer_file(buffer_list, buffer_filename, "question-detail-delimiter")

def update_buffer_to_db(buffer_list, tm):
    question_id_list = map(lambda question: question[0], buffer_list)
    sql = "UPDATE ZHIHU_QUESTION_ID SET LAST_VISIT = %s WHERE QUESTION_ID = %s"
    ts = get_current_timestamp()
    args = map(lambda question_id: (ts, question_id), question_id_list)
    print "......Update sql:%s, args:%s" % (sql, args)
    tm.execute_many_sql(sql, args)

