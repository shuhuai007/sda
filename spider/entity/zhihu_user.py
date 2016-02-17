#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, time, platform, random
import re, json, cookielib

# requirements
import requests

try:
    from bs4 import BeautifulSoup
except:
    import BeautifulSoup


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

    def get_user_id(self):
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
        if self._url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            data_id = soup.find("button", class_="zg-btn zg-btn-follow zm-rich-follow-btn")[
                'data-id']
            return data_id

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
            followees_num = int(soup.find("div", class_="zm-profile-side-following zg-clear")
                                .find("a").strong.string)
            return followees_num

    def get_followers_num(self):
        if self._url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            followers_num = int(soup.find("div", class_="zm-profile-side-following zg-clear")
                                .find_all("a")[1].strong.string)
            return followers_num

    def get_agree_num(self):
        if self._url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            agree_num = int(soup.find("span", class_="zm-profile-header-user-agree").strong.string)
            return agree_num

    def get_thanks_num(self):
        if self._url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            thanks_num = int(
                soup.find("span", class_="zm-profile-header-user-thanks").strong.string)
            return thanks_num

    def get_asks_num(self):
        if self._url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            asks_num = int(soup.find_all("span", class_="num")[0].string)
            return asks_num

    def get_answers_num(self):
        if self._url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            answers_num = int(soup.find_all("span", class_="num")[1].string)
            return answers_num

    def get_collections_num(self):
        if self._url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            collections_num = int(soup.find_all("span", class_="num")[3].string)
            return collections_num

    def get_followees(self):
        if self._url == None:
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
                r = requests.get(followee_url)

                soup = BeautifulSoup(r.content)
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
                        hash_id = re.findall("hash_id&quot;: &quot;(.*)&quot;},", r.text)[0]
                        params = json.dumps(
                            {"offset": offset, "order_by": "created", "hash_id": hash_id})
                        data = {
                            '_xsrf': _xsrf,
                            'method': "next",
                            'params': params
                        }
                        header = {
                            'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                            'Host': "www.zhihu.com",
                            'Referer': followee_url
                        }

                        r_post = requests.post(post_url, data=data, headers=header)

                        followee_list = r_post.json()["msg"]
                        for j in xrange(min(followees_num - i * 20, 20)):
                            followee_soup = BeautifulSoup(followee_list[j])
                            user_link = followee_soup.find("h2", class_="zm-list-content-title").a
                            yield User(user_link["href"], user_link.string.encode("utf-8"))

    def get_followers(self):
        if self._url == None:
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
                r = requests.get(follower_url)

                soup = BeautifulSoup(r.content)
                for i in xrange((followers_num - 1) / 20 + 1):
                    if i == 0:
                        user_url_list = soup.find_all("h2", class_="zm-list-content-title")
                        for j in xrange(min(followers_num, 20)):
                            yield User(user_url_list[j].a["href"],
                                       user_url_list[j].a.string.encode("utf-8"))
                    else:
                        post_url = "http://www.zhihu.com/node/ProfileFollowersListV2"
                        _xsrf = soup.find("input", attrs={'name': '_xsrf'})["value"]
                        offset = i * 20
                        hash_id = re.findall("hash_id&quot;: &quot;(.*)&quot;},", r.text)[0]
                        params = json.dumps(
                            {"offset": offset, "order_by": "created", "hash_id": hash_id})
                        data = {
                            '_xsrf': _xsrf,
                            'method': "next",
                            'params': params
                        }
                        header = {
                            'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                            'Host': "www.zhihu.com",
                            'Referer': follower_url
                        }
                        r_post = requests.post(post_url, data=data, headers=header)

                        follower_list = r_post.json()["msg"]
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


if __name__ == '__main__':
    url = "http://www.zhihu.com/people/jixin"
    user = User(url)
    print "user's id:%s" % user.get_user_id()

