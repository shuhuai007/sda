#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import gzip
import StringIO
import ConfigParser

from zhihu_constants import *

REFER_DICT = {
    LEVEL1_TOPICS_URL : 'http://www.zhihu.com/',
    LEVEL2_TOPICS_URL : 'https://www.zhihu.com/topics'
}

def get_content(to_url):
    cookie = get_cookie()

    headers = get_headers(cookie, to_url)

    req = urllib2.Request(
        url = to_url,
        headers = headers
    )

    try:
        opener = urllib2.build_opener(urllib2.ProxyHandler())
        urllib2.install_opener(opener)

        page = urllib2.urlopen(req, timeout = 15)

        headers = page.info()
        content = page.read()
    except Exception,e:
        # if count % 1 == 0:
        #     print str(count) + ", Error: " + str(e) + " URL: " + to_url
        return "FAIL"

    if page.info().get('Content-Encoding') == 'gzip':
        data = StringIO.StringIO(content)
        gz = gzip.GzipFile(fileobj=data)
        content = gz.read()
        gz.close()

    return content

def post(to_url, post_data):
    cookie = get_cookie()

    headers = get_headers(cookie, to_url)


    req = urllib2.Request(to_url, post_data, headers)
    resp = urllib2.urlopen(req)
    content = resp.read()
    if resp.info().get('Content-Encoding') == 'gzip':
        data = StringIO.StringIO(content)
        gz = gzip.GzipFile(fileobj=data)
        content = gz.read()
        gz.close()

    return content

def get_xsrf_from_cookie(cookie):
    cookie_list = cookie.split(';')
    # print "\n\ncookie_list:%s" % cookie_list

    for cookie_item in cookie_list:
        cookie_key = cookie_item.split('=')[0].strip()
        cookie_value = cookie_item.split('=')[1]
        # print "\n\ncookie_key:%s" % cookie_key
        # print "\n\ncookie_value:%s" % cookie_value

        if cookie_key == '_xsrf':
            return cookie_value
    print "\n\n_xsrf doesn't exist in cookie"
    return ""

def get_xsrf():
    return get_xsrf_from_cookie(get_cookie())

def get_cookie():
    cf = ConfigParser.ConfigParser()
    cf.read("config.ini")
    cookie = cf.get("cookie", "cookie")
    return cookie

def get_headers(cookie, to_url):
    headers = {
        'Cookie':cookie,
        'Host':'www.zhihu.com',
        'Referer':REFER_DICT[to_url],
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Accept-Encoding':'gzip'
    }
    return headers
