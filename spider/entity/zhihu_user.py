#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import platform
import re
import json
import cookielib
from Queue import Queue
from urllib import urlencode


# requirements
import requests

import sys
sys.path.append("..")
import zhihu_util

try:
    from bs4 import BeautifulSoup
except:
    import BeautifulSoup

from pybloom import BloomFilter

USER_URL = "http://www.zhihu.com/people/{0}"
THREAD_COUNT = 1


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
        r = requests.get(self._url)
        soup = BeautifulSoup(r.content, "html.parser")
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
        if self._url == None:
            print "I'm anonymous user."
            return 'unknown'
        else:
            if self.soup == None:
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
        if self._url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
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
            if self.soup == None:
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
            if self.soup == None:
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
            if self.soup == None:
                self.parser()
            soup = self.soup
            try:
                thanks_num = int(
                    soup.find("span", class_="zm-profile-header-user-thanks").strong.string)
                return thanks_num
            except:
                return 0

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
                soup = BeautifulSoup(r, "html.parser")
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
                            followee_soup = BeautifulSoup(followee_list[j], "html.parser")
                            user_link = followee_soup.find("h2", class_="zm-list-content-title").a
                            yield User(user_link["href"], user_link.string.encode("utf-8"))

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
                soup = BeautifulSoup(r, "html.parser")
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
                        # print "...data:%s" % data
                        # print "...r_post:%s" % r_post
                        follower_list = json.loads(r_post)["msg"]
                        for j in xrange(min(followers_num - i * 20, 20)):
                            follower_soup = BeautifulSoup(follower_list[j])
                            user_link = follower_soup.find("h2", class_="zm-list-content-title").a
                            yield User(user_link["href"], user_link.string.encode("utf-8"))

    def get_asks(self):
        """
            By ecsys (https://github.com/ecsys)
            增加了获取某用户所有赞过答案的功能 #29
            (https://github.com/egrcc/zhihu-python/pull/29)
        """
        if self._url == None:
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

                    soup = BeautifulSoup(r.content)
                    for question in soup.find_all("a", class_="question_link"):
                        url = "http://www.zhihu.com" + question["href"]
                        title = question.string.encode("utf-8")
                        yield Question(url, title)

    def get_answers(self):
        if self._url == None:
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
                    soup = BeautifulSoup(r.content)
                    for answer in soup.find_all("a", class_="question_link"):
                        question_url = "http://www.zhihu.com" + answer["href"][0:18]
                        question_title = answer.string.encode("utf-8")
                        question = Question(question_url, question_title)
                        yield Answer("http://www.zhihu.com" + answer["href"], question, self)

    def get_collections(self):
        if self._url == None:
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

                    soup = BeautifulSoup(r.content)
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
        if self._url == None:
            print "I'm an anonymous user."
            return
            yield
        else:
            r = requests.get(self._url)
            soup = BeautifulSoup(r.content)
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

    def get_posts_num(self):
        # TODO (zj)
        pass

    def get_logs_num(self):
        # TODO (zj)
        pass

    def get_focus_topics_num(self):
        # TODO (zj)
        pass

    def get_browse_num(self):
        # TODO (zj)
        pass

    def get_fields(self):
        # TODO (zj)
        return self.get_user_name(), self.get_user_title(), self.get_user_agree_num()

def init_bloom_filter():
    f = BloomFilter(capacity=1000, error_rate=0.001)
    # TODO (zj) : need get initial info from datasource
    return f


def flush_buffer(write_buffer):
    # TODO (zj)
    print "...begin write buffer into disk..."

    data_dir = zhihu_util.get_data_directory("user")
    buffer_filename = "%s/user-%s" % (data_dir, int(time.time()))
    zhihu_util.write_buffer_file(write_buffer, buffer_filename, "\001")


def consume(filter, queue, index, loops):
    print "Thread[%s]consume the queue..." % str(index)
    count = 0
    write_buffer_list = []

    while count < loops and not queue.empty():
        people_url = USER_URL.format(queue.get())
        print "...people_url:%s" % people_url
        user = User(people_url)

        suffix = user.get_url_suffix()
        if suffix in filter:
            continue
        filter.add(suffix)
        write_buffer_list.append(user.get_fields())

        for follower in user.get_followers():
            if follower.get_url_suffix() in filter:
                continue
            filter.add(suffix)
            write_buffer_list.append(follower.get_fields())

        if len(write_buffer_list) >= 10:
            flush_buffer(write_buffer_list)
            write_buffer_list = []

        for followee in user.get_followees():
            queue.put(followee.get_url_suffix())

        count += 1

    flush_buffer(write_buffer_list)


def main():
    filter = init_bloom_filter()

    # url = "http://www.zhihu.com/people/jixin"
    # url = "http://www.zhihu.com/people/jie-28"
    # user = User(url)
    #
    # followers = user.get_followers()
    # for user in followers:
    #     print "follower: %s" % user.get_user_name()
    #
    # followees = user.get_followees()
    # for user in followees:
    #     print "followee: %s" % user.get_user_name()
    #
    # print "user data id:%s" % user.get_data_id()
    #
    # print "user name:%s" % user.get_user_name()
    # print "user title:%s" % user.get_user_title()
    # print "user gender:%s" % user.get_gender()
    #
    # print "user location:%s" % user.get_location()
    # print "user business:%s" % user.get_business()
    #
    # print "user employment:%s" % user.get_employment()
    # print "user position:%s" % user.get_position()
    #
    # print "user education:%s" % user.get_education()
    # print "user education extra:%s" % user.get_education_extra()
    #
    # print "user agree num:%s" % user.get_user_agree_num()
    # print "user thanks num:%s" % user.get_user_thanks_num()
    #
    # print "asks num:%s" % user.get_asks_num()
    # print "answers num:%s" % user.get_answers_num()
    # print "posts num:%s" % user.get_posts_num()
    # print "collections num:%s" % user.get_collections_num()
    # print "logs num:%s" % user.get_logs_num()
    #
    # print "followees num:%s" % user.get_followees_num()
    # print "followers num:%s" % user.get_followers_num()
    # print "focus topics num:%s" % user.get_focus_topics_num()
    # print "browse num:%s" % user.get_browse_num()

    # exit()
    from zhihu_thread import MyThread
    threads = []
    queue = Queue()

    user_seed = "jixin"
    user_seed = "jie-28"

    queue.put_nowait(user_seed)
    print "Start, queue's size:%s" % queue.qsize()

    loops = 100
    for i in range(THREAD_COUNT):
        t = MyThread(consume, (filter, queue, i, loops), consume.__name__)
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print "End, queue's size:%s" % queue.qsize()

    print "All Done"


if __name__ == '__main__':
    main()
