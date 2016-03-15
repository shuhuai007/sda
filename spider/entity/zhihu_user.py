#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')
from spider import zhihu_util

reload(sys)
sys.setdefaultencoding('utf-8')

import math
import time
import platform
import re
import json
import requests
from Queue import Queue
from urllib import urlencode
from pybloom import BloomFilter


USER_URL = "http://www.zhihu.com/people/{0}"
THREAD_COUNT = 10
GRAPH_DEEP_LEVEL = 1000

USER_FIELD_DELIMITER = "\001"
USER_FILE_DELIMITER = "ufdelimiter"


class User:
    # session = None
    soup = None

    def __init__(self, user_url, user_id=None):
        if user_url is None:
            self.user_id = "匿名用户"
        elif not user_url.startswith('www.zhihu.com/people', user_url.index('//') + 2):
            raise ValueError("\"" + user_url + "\"" + " : it isn't a user url.")
        else:
            self._url = user_url
            if user_id:
                self.user_id = user_id

    def parser(self):
        # r = requests.get(self._url)
        resp_content = zhihu_util.get_content(self._url)
        soup = zhihu_util.get_soup(resp_content)
        self.soup = soup

    def get_url_suffix(self):
        return self._url.split("/")[-1]

    def get_user_name(self):
        if self._url is None:
            # print "I'm anonymous user."
            if platform.system() == 'Windows':
                return "匿名用户".decode('utf-8').encode('gbk')
            else:
                return "匿名用户"
        else:
            if hasattr(self, "user_id"):
                if platform.system() == 'Windows':
                    return self.user_id.decode('utf-8').encode('gbk')
                else:
                    return self.user_id
            else:
                if self.soup is None:
                    self.parser()
                soup = self.soup
                user_id = soup.find("div", class_="title-section ellipsis") \
                    .find("span", class_="name").string.encode("utf-8")
                self.user_id = user_id
                if platform.system() == 'Windows':
                    return user_id.decode('utf-8').encode('gbk')
                else:
                    return user_id

    def get_data_id(self):
        """
            By yannisxu (https://github.com/yannisxu)
            增加获取知乎 data-id 的方法来确定标识用户的唯一性 #24
            (https://github.com/egrcc/zhihu-python/pull/24)
        """
        if self._url is None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                data_id = soup.find("button", class_="zg-btn zg-btn-follow zm-rich-follow-btn")[
                    'data-id']
                return data_id
            except:
                return 0

    def get_gender(self):
        """
            By Mukosame (https://github.com/mukosame)
            增加获取知乎识用户的性别

        """
        if self._url is None:
            print "I'm anonymous user."
            return 'unknown'
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                gender = str(soup.find("span", class_="item gender").i)
                if (gender == '<i class="icon icon-profile-female"></i>'):
                    return 'female'
                else:
                    return 'male'
            except:
                return 'unknown'

    def get_followees_num(self):
        if self._url is None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                followees_num = int(soup.find("div", class_="zm-profile-side-following zg-clear")
                                    .find("a").strong.string)
                return followees_num
            except:
                return 0

    def get_followers_num(self):
        if self._url is None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                followers_num = int(soup.find("div", class_="zm-profile-side-following zg-clear")
                                    .find_all("a")[1].strong.string)
                return followers_num
            except:
                return 0

    def get_agree_num(self):
        if self._url is None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                agree_num = int(soup.find("span", class_="zm-profile-header-user-agree").strong.string)
                return agree_num
            except:
                return 0

    def get_thanks_num(self):
        if self._url is None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                thanks_num = int(
                    soup.find("span", class_="zm-profile-header-user-thanks").strong.string)
                return thanks_num
            except:
                return 0

    def get_followees(self):
        if self._url is None:
            print "I'm anonymous user."
            return
            yield
        else:
            followees_num = self.get_followees_num()
            if followees_num == 0:
                return
                yield
            else:
                followee_url = self._url + "/followees"
                r = zhihu_util.get_content(followee_url)
                # print "r:%s" % r
                soup = zhihu_util.get_soup(r)
                for i in xrange((followees_num - 1) / 20 + 1):
                    if i == 0:
                        user_url_list = soup.find_all("h2", class_="zm-list-content-title")
                        for j in xrange(min(followees_num, 20)):
                            yield User(user_url_list[j].a["href"],
                                       user_url_list[j].a.string.encode("utf-8"))
                    else:
                        post_url = "http://www.zhihu.com/node/ProfileFolloweesListV2"
                        _xsrf = soup.find("input", attrs={'name': '_xsrf'})["value"]
                        offset = i * 20
                        hash_id = re.findall("hash_id&quot;: &quot;(.*)&quot;},", r)[0]
                        params = json.dumps(
                            {"offset": offset, "order_by": "created", "hash_id": hash_id})
                        data = {
                            '_xsrf': _xsrf,
                            'method': "next",
                            'params': params
                        }
                        post_data = urlencode(data)
                        r_post = zhihu_util.post(post_url, post_data)

                        followee_list = json.loads(r_post)["msg"]
                        for j in xrange(min(followees_num - i * 20, 20)):
                            try:
                                followee_soup = zhihu_util.get_soup(followee_list[j])

                                user_link = followee_soup.find("h2", class_="zm-list-content-title").a
                                yield User(user_link["href"], user_link.string.encode("utf-8"))
                            except:
                                print("...get followee error ,just skip...")
                                return
                                yield

    def get_followers(self):
        if self._url is None:
            print "I'm anonymous user."
            return
            yield
        else:
            followers_num = self.get_followers_num()
            if followers_num == 0:
                return
                yield
            else:
                follower_url = self._url + "/followers"
                r = zhihu_util.get_content(follower_url)
                soup = zhihu_util.get_soup(r)
                for i in xrange((followers_num - 1) / 20 + 1):
                    if i == 0:
                        user_url_list = soup.find_all("h2", class_="zm-list-content-title")
                        # print "...user_url_list's len:%s" % len(user_url_list)
                        for j in xrange(min(followers_num, 20)):
                            yield User(user_url_list[j].a["href"],
                                       user_url_list[j].a.string.encode("utf-8"))
                    else:
                        post_url = "http://www.zhihu.com/node/ProfileFollowersListV2"
                        _xsrf = soup.find("input", attrs={'name': '_xsrf'})["value"]
                        offset = i * 20
                        hash_id = re.findall("hash_id&quot;: &quot;(.*)&quot;},", r)[0]
                        params = json.dumps(
                            {"offset": offset, "order_by": "created", "hash_id": hash_id})
                        data = {
                            '_xsrf': _xsrf,
                            'method': "next",
                            'params': params
                        }
                        post_data = urlencode(data)
                        r_post = zhihu_util.post(post_url, post_data)
                        if r_post == 'FAIL':
                            continue
                        follower_list = json.loads(r_post)["msg"]
                        for j in xrange(min(followers_num - i * 20, 20)):
                            try:
                                follower_soup = zhihu_util.get_soup(follower_list[j])
                                user_link = follower_soup.find("h2", class_="zm-list-content-title").a
                                yield User(user_link["href"], user_link.string.encode("utf-8"))
                            except:
                                print "...Get follower error, just skip..."
                                return
                                yield

    def get_asks(self):
        """
            By ecsys (https://github.com/ecsys)
            增加了获取某用户所有赞过答案的功能 #29
            (https://github.com/egrcc/zhihu-python/pull/29)
        """
        if self._url is None:
            print "I'm anonymous user."
            return
            yield
        else:
            asks_num = self.get_asks_num()
            if asks_num == 0:
                return
                yield
            else:
                for i in xrange((asks_num - 1) / 20 + 1):
                    ask_url = self._url + "/asks?page=" + str(i + 1)
                    r = requests.get(ask_url)

                    soup = zhihu_util.get_soup(r.content)
                    for question in soup.find_all("a", class_="question_link"):
                        url = "http://www.zhihu.com" + question["href"]
                        title = question.string.encode("utf-8")
                        yield Question(url, title)

    def get_answers(self):
        if self._url is None:
            print "I'm anonymous user."
            return
            yield
        else:
            answers_num = self.get_answers_num()
            if answers_num == 0:
                return
                yield
            else:
                for i in xrange((answers_num - 1) / 20 + 1):
                    answer_url = self._url + "/answers?page=" + str(i + 1)
                    r = requests.get(answer_url)
                    soup = zhihu_util.get_soup(r.content)
                    for answer in soup.find_all("a", class_="question_link"):
                        question_url = "http://www.zhihu.com" + answer["href"][0:18]
                        question_title = answer.string.encode("utf-8")
                        question = Question(question_url, question_title)
                        yield Answer("http://www.zhihu.com" + answer["href"], question, self)

    def get_collections(self):
        if self._url is None:
            print "I'm anonymous user."
            return
            yield
        else:
            collections_num = self.get_collections_num()
            if collections_num == 0:
                return
                yield
            else:
                for i in xrange((collections_num - 1) / 20 + 1):
                    collection_url = self._url + "/collections?page=" + str(i + 1)

                    r = requests.get(collection_url)

                    soup = zhihu_util.get_soup(r.content)
                    for collection in soup.find_all("div",
                                                    class_="zm-profile-section-item zg-clear"):
                        url = "http://www.zhihu.com" + \
                              collection.find("a", class_="zm-profile-fav-item-title")["href"]
                        name = collection.find("a",
                                               class_="zm-profile-fav-item-title").string.encode(
                            "utf-8")
                        yield Collection(url, name, self)

    def get_likes(self):
        # This function only handles liked answers, not including zhuanlan articles
        if self._url is None:
            print "I'm an anonymous user."
            return
            yield
        else:
            r = requests.get(self._url)
            soup = zhihu_util.get_soup(r.content)
            # Handle the first liked item
            first_item = soup.find("div",
                                   attrs={'class': 'zm-profile-section-item zm-item clearfix'})
            first_item = first_item.find("div", attrs={
                'class': 'zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main'})
            if u"赞同了回答" in str(first_item):
                first_like = first_item.find("a")['href']
                yield Answer("http://www.zhihu.com" + first_like)
            # Handle the rest liked items
            post_url = self._url + "/activities"
            start_time = \
                soup.find("div", attrs={'class': 'zm-profile-section-item zm-item clearfix'})[
                    "data-time"]
            _xsrf = soup.find("input", attrs={'name': '_xsrf'})["value"]
            data = {
                'start': start_time,
                '_xsrf': _xsrf,
            }
            header = {
                'Host': "www.zhihu.com",
                'Referer': self._url,
                'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            }
            r = requests.post(post_url, data=data, headers=header)
            response_size = r.json()["msg"][0]
            response_html = r.json()["msg"][1]
            while response_size > 0:
                all_liked_answers = re.findall(
                    u"\u8d5e\u540c\u4e86\u56de\u7b54\n\n<a class=\"question_link\" target=\"_blank\" href=\"\/question\/\d{8}\/answer\/\d{8}",
                    response_html)
                liked_answers = list(set(all_liked_answers))
                liked_answers.sort(key=all_liked_answers.index)
                for i in xrange(len(liked_answers)):
                    answer_url = "http://www.zhihu.com" + liked_answers[i][54:]
                    yield Answer(answer_url)
                data_times = re.findall(r"data-time=\"\d+\"", response_html)
                if len(data_times) != response_size:
                    print "读取activities栏时间信息时发生错误，可能因为某答案中包含data-time信息"
                    return
                    yield
                latest_data_time = re.search(r"\d+", data_times[response_size - 1]).group()
                data = {
                    'start': latest_data_time,
                    '_xsrf': _xsrf,
                }
                r = requests.post(post_url, data=data, headers=header)
                response_size = r.json()["msg"][0]
                response_html = r.json()["msg"][1]
            return
            yield

    def get_user_title(self):
        if self._url is None:
            print "I'm anonymous user."
            return 'unknown'
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                user_title = soup.find("div", class_="title-section ellipsis")\
                    .find("span", class_="bio").string.encode("utf-8")
                if platform.system() == 'Windows':
                    return user_title.decode('utf-8').encode('gbk')
                else:
                    return user_title
            except:
                return "unknown"

    def get_location(self):
        if self._url is None:
            print "I'm anonymous user."
            return 'unknown'
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                location = soup.find("div", attrs={'data-name': 'location'})\
                               .find("span", attrs={'class': 'location item'})\
                               .get('title').encode("utf-8")
                if platform.system() == 'Windows':
                    return location.decode('utf-8').encode('gbk')
                else:
                    return location
            except:
                return "unknown"

    def get_business(self):
        if self._url is None:
            print "I'm anonymous user."
            return 'unknown'
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                business = soup.find("div", attrs={'data-name': 'location'}) \
                    .find("span", attrs={'class': 'business item'}) \
                    .get('title').encode("utf-8")
                if platform.system() == 'Windows':
                    return business.decode('utf-8').encode('gbk')
                else:
                    return business
            except:
                return "unknown"

    def get_employment(self):
        if self._url is None:
            print "I'm anonymous user."
            return 'unknown'
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                employment = soup.find("div", attrs={'data-name': 'employment'}) \
                    .find("span", attrs={'class': 'employment item'}) \
                    .get('title').encode("utf-8")
                if platform.system() == 'Windows':
                    return employment.decode('utf-8').encode('gbk')
                else:
                    return employment
            except:
                return "unknown"

    def get_position(self):
        if self._url is None:
            print "I'm anonymous user."
            return 'unknown'
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                position = soup.find("div", attrs={'data-name': 'employment'}) \
                    .find("span", attrs={'class': 'position item'}) \
                    .get('title').encode("utf-8")
                if platform.system() == 'Windows':
                    return position.decode('utf-8').encode('gbk')
                else:
                    return position
            except:
                return "unknown"

    def get_education(self):
        if self._url is None:
            print "I'm anonymous user."
            return 'unknown'
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                position = soup.find("div", attrs={'data-name': 'education'}) \
                    .find("span", attrs={'class': 'education item'}) \
                    .get('title').encode("utf-8")
                if platform.system() == 'Windows':
                    return position.decode('utf-8').encode('gbk')
                else:
                    return position
            except:
                return "unknown"

    def get_education_extra(self):
        if self._url is None:
            print "I'm anonymous user."
            return 'unknown'
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                position = soup.find("div", attrs={'data-name': 'education'}) \
                    .find("span", attrs={'class': 'education-extra item'}) \
                    .get('title').encode("utf-8")
                if platform.system() == 'Windows':
                    return position.decode('utf-8').encode('gbk')
                else:
                    return position
            except:
                return "unknown"

    def get_user_agree_num(self):
        if self._url is None:
            print "I'm anonymous user."
            return '0'
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                user_agree_num = soup.find("span", attrs={'class': 'zm-profile-header-user-agree'})\
                    .find("strong").get_text().encode("utf-8")
                return user_agree_num
            except:
                return "0"

    def get_user_thanks_num(self):
        if self._url is None:
            print "I'm anonymous user."
            return '0'
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                user_agree_num = soup.find("span", attrs={'class': 'zm-profile-header-user-thanks'})\
                    .find("strong").get_text().encode("utf-8")
                return user_agree_num
            except:
                return "0"

    def get_asks_num(self):
        if self._url is None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                asks_num = int(soup.find_all("span", class_="num")[0].string)
                return asks_num
            except:
                return 0

    def get_answers_num(self):
        if self._url is None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                answers_num = int(soup.find_all("span", class_="num")[1].string)
                return answers_num
            except:
                return 0

    def get_posts_num(self):
        if self._url is None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                answers_num = int(soup.find_all("span", class_="num")[2].string)
                return answers_num
            except:
                return 0

    def get_collections_num(self):
        if self._url is None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                collections_num = int(soup.find_all("span", class_="num")[3].string)
                return collections_num
            except:
                return 0

    def get_logs_num(self):
        if self._url is None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                collections_num = int(soup.find_all("span", class_="num")[4].string)
                return collections_num
            except:
                return 0

    def get_focus_topics_num(self):
        if self._url is None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                focus_topics_num = int(soup.find("div", class_="zm-side-section-inner zg-clear")
                                       .find("a").strong.string[0])
                return focus_topics_num
            except:
                return 0

    def get_browse_num(self):
        # zu-main-sidebar, zm-profile-side-section,
        if self._url is None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
            try:
                browse_num = int(soup.find("div", class_="zu-main-sidebar")
                                     .find_all("div", class_="zm-profile-side-section")[2]
                                     .find("span").strong.string)
                return browse_num
            except:
                return 0

    def get_fields(self):
        return self. get_url_suffix(), self.get_data_id(), self.get_user_name(),\
            self.get_user_title(), self.get_gender(),\
            self.get_location(), self.get_business(),\
            self.get_employment(), self.get_position(),\
            self.get_education(), self.get_education_extra(),\
            self.get_user_agree_num(), self.get_user_thanks_num(),\
            self.get_asks_num(), self.get_answers_num(),\
            self.get_posts_num(), self.get_collections_num(),\
            self.get_logs_num(), self.get_followees_num(),\
            self.get_followers_num(), self.get_focus_topics_num(),\
            self.get_browse_num()

    def generate_user_seeds(self, request_times=1, user_accessed_set=None):
        if self._url is None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup is None:
                self.parser()
            soup = self.soup
        seed_list = []
        for i in range(request_times):
            post_url = "https://www.zhihu.com/lookup/suggest_member"
            _xsrf = soup.find("input", attrs={'name': '_xsrf'})["value"]
            data = {
                'ids': ",,",
                '_xsrf': _xsrf
            }
            post_data = urlencode(data)
            r_post = zhihu_util.post(post_url, post_data)
            suggent_member_list = json.loads(r_post)["msg"]
            for suggent_member in suggent_member_list:
                suggent_member_soup = zhihu_util.get_soup(suggent_member)
                suggent_member_str = suggent_member_soup.find("a", class_="image-link")\
                                                        .get("href").split("/")[-1]
                seed_list.append(suggent_member_str)

        seed_set = set(seed_list)
        if user_accessed_set:
            seed_set.difference_update(user_accessed_set)
        return seed_set


def init_bloom_filter():
    print "...init bloom filter..."
    write_bf = generate_write_bloomfilter("user", 10000000)
    return write_bf

def generate_write_bloomfilter(dir_name, capacity=1000000, error_rate=0.01):
    bf = BloomFilter(capacity, error_rate)
    data_dir = zhihu_util.get_data_directory(dir_name)
    data_file_list = zhihu_util.get_file_list(data_dir)
    for data_file in data_file_list:
        # read url_suffix from data file
        with open(data_file, "r") as file_object:
            for line in file_object:
                url_suffix = line.split(USER_FIELD_DELIMITER)[0]
                if url_suffix.strip() != '':
                    # print "......url suffix:%s added into bloom filter" % url_suffix
                    bf.add(str(url_suffix))
    return bf

def flush_buffer(write_buffer, suffix, ts, thread_index, mode="finish"):
    print "...write buffer into disk..."
    data_dir = zhihu_util.get_data_directory("user")
    buffer_filename = "%s/%s%s-%s-%s" % (data_dir, suffix, USER_FILE_DELIMITER, int(ts),
                                         thread_index)
    if mode == "doing":
        buffer_filename += ".doing"
    zhihu_util.write_buffer_file(write_buffer, buffer_filename, USER_FIELD_DELIMITER)

def consume(lock, bf_lock, bloomfilter, user_accessed_set, queue, thread_index, loops):
    print "...Thread[%s]consume the queue..." % str(thread_index)
    count = 0

    while count < loops:
        suffix = queue.get()

        with lock:
            if suffix in user_accessed_set:
                continue

        people_url = USER_URL.format(suffix)
        print "...people_url:%s" % people_url
        user = User(people_url)

        write_buffer_list = []
        timestamp = time.time()

        total_followers = user.get_followers_num()
        sleep_delta = 0
        for i, follower in enumerate(user.get_followers()):
            print "...Thread[%s], user %s's %s follower:%s, total:%s" % \
                  (thread_index, suffix, str(i), follower.get_url_suffix(), total_followers)
            with bf_lock:
                if follower.get_url_suffix() in bloomfilter:
                    print "...Thread[%s], %s already exist in bloom filter" % \
                          (thread_index, follower.get_url_suffix())
                    continue
                bloomfilter.add(follower.get_url_suffix())
            write_buffer_list.append(follower.get_fields())
            print "...Thread[%s], bloom filter add %s, write buffer's size:%s" % \
                  (thread_index, follower.get_url_suffix(), len(write_buffer_list))

            if len(write_buffer_list) >= 1000:
                flush_buffer(write_buffer_list, suffix, timestamp, thread_index, mode="doing")
                write_buffer_list = []
                print "...Thread[%s], at present, bloom filter's size:%s" % \
                      (thread_index, bloomfilter.count)
            if sleep_delta >= 500:
                time.sleep(1)
                print "...Thread[%s] sleep 1 second..." % thread_index
                sleep_delta = 0
            else:
                sleep_delta += 1

        flush_buffer(write_buffer_list, suffix, timestamp, thread_index)

        with lock:
            for followee in user.get_followees():
                if followee in user_accessed_set:
                    print "...Thread[%s], user %s's followee %s exist in user_access_set" % \
                          (thread_index, suffix, followee.get_url_suffix())
                    continue
                queue.put(followee.get_url_suffix())
                print "...Thread[%s], user %s's followee %s added into queue, queue size:%s" % \
                      (thread_index, suffix, followee.get_url_suffix(), queue.qsize())
            user_accessed_set.add(suffix)

        count += 1

def init_user_access():
    data_dir = zhihu_util.get_data_directory("user")
    filenames = zhihu_util.get_file_names(data_dir)
    result_list = [filename.split(USER_FILE_DELIMITER)[0] for filename in filenames]
    return set(result_list)

def main():
    f = init_bloom_filter()
    print "bloom filter's count:%s" % f.count

    user_accessed_set = init_user_access()
    print "user accessed set:%s" % user_accessed_set

    from zhihu_thread import MyThread
    threads = []
    queue = Queue()

    url = USER_URL.format("jie-28")
    user_seeds = User(url).generate_user_seeds(int(math.ceil(THREAD_COUNT)), user_accessed_set)

    for user_seed in user_seeds:
        queue.put_nowait(user_seed)
    print "Start, user seeds:%s " % user_seeds

    import threading
    lock = threading.Lock()
    bf_lock = threading.Lock()
    for i in range(THREAD_COUNT):
        t = MyThread(consume, (lock, bf_lock, f, user_accessed_set, queue, i, GRAPH_DEEP_LEVEL),
                     consume.__name__)
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print "End, queue's size:%s" % queue.qsize()

    print "All Done"


if __name__ == '__main__':
    main()
