#! /usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re


def store_cookie(session_cookies):
    cookie_list = []
    for (k, v) in session_cookies.iteritems():
        cookie_list.append(k + '=' + v)
    print "; ".join(cookie_list)

def login():
    url = 'http://www.zhihu.com'
    login_url = url+'/login/email'
    login_data = {
        'email': 'zhoujie338@126.com',
        'password': 'zhoujie2014',
        'rememberme': 'true',
    }
    headers_base = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
        'Connection': 'keep-alive',
        'Host': 'www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
        'Referer': 'http://www.zhihu.com/',
    }

    s = requests.session()

    def get_xsrf(url_link=None):
        r = s.get(url_link, headers=headers_base)
        xsrf = re.search(r'(?<=name="_xsrf" value=")[^"]*(?="/>)', r.text)
        if xsrf is None:
            return ''
        else:
            return xsrf.group(0)

    login_data['_xsrf'] = get_xsrf(url).encode('utf-8')

    res = s.post(login_url, headers=headers_base, data=login_data)
    print res.status_code

    test_url = 'http://www.zhihu.com/people/jie-28/followees'
    res = s.get(test_url, headers=headers_base, cookies=res.cookies)

    if str(res.status_code) == '200':
        print 'session cookies', requests.utils.dict_from_cookiejar(s.cookies)
        session_cookies = requests.utils.dict_from_cookiejar(s.cookies)
        store_cookie(session_cookies)


def generate_captcha(login_data, s):
    captcha_url = 'http://www.zhihu.com/captcha.gif'
    captcha = s.get(captcha_url, stream=True)
    print captcha
    f = open('captcha.gif', 'wb')
    for line in captcha.iter_content(10):
        f.write(line)
    f.close()
    print u'输入验证码:'
    captcha_str = raw_input()
    login_data['captcha'] = captcha_str


def work():
    login()

if __name__ == '__main__':
    work()
