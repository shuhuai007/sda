#! /usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re
from bs4 import BeautifulSoup

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

    def get_xsrf(url=None):
        r = s.get(url, headers=headers_base)
        xsrf = re.search(r'(?<=name="_xsrf" value=")[^"]*(?="/>)', r.text)
        if xsrf == None:
            return ''
        else:
            return xsrf.group(0)

    xsrf = get_xsrf(url)
    login_data['_xsrf'] = xsrf.encode('utf-8')

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

    res = s.post(login_url, headers=headers_base, data=login_data)
    print res.status_code
    m_cookies = res.cookies


    test_url = 'http://www.zhihu.com/people/jie-28/followees'
    res = s.get(test_url, headers=headers_base, cookies=m_cookies)

    def get_users(content=None):
        users = re.search(r'<a title="*>', content)
        print users.group(0)

    print "response:%s" % res.text
    get_users(res.text)


def work():
    login()

if __name__ == '__main__':
    work()
