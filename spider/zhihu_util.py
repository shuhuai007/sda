#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import gzip
import StringIO
import ConfigParser

from urllib import urlencode

def get_content(toUrl):
    cf = ConfigParser.ConfigParser()
    cf.read("config.ini")
    cookie = cf.get("cookie", "cookie")

    headers = {
        'Cookie': cookie,
        'Host':'www.zhihu.com',
        'Referer':'http://www.zhihu.com/',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Accept-Encoding':'gzip'
    }

    req = urllib2.Request(
        url = toUrl,
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
        #     print str(count) + ", Error: " + str(e) + " URL: " + toUrl
        return "FAIL"

    if page.info().get('Content-Encoding') == 'gzip':
        data = StringIO.StringIO(content)
        gz = gzip.GzipFile(fileobj=data)
        content = gz.read()
        gz.close()

    return content

def post(toUrl, level1_topic_id, hash_id, offset=20):
    cf = ConfigParser.ConfigParser()
    cf.read("config.ini")
    cookie = cf.get("cookie", "cookie")


    headers = {
        'Cookie': cookie,
        'Host':'www.zhihu.com',
        'Referer':'https://www.zhihu.com/topics',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Accept-Encoding':'gzip'
    }

    post_dict = {}
    post_dict["method"] = "next"

    # post_dict["params"] = '{"topic_id":253,"offset":40,"hash_id":"dced108689287057f5cc3b5e85cb8289"}'
    params_dict = '{' \
                    '"topic_id":' + str(level1_topic_id) + ',' \
                    '"offset":' + str(offset) + ',' \
                    '"hash_id":' + '"' + str(hash_id) + '"' \
                  '}'

    post_dict["params"] = params_dict
    print "\n\nparams_dict:%s" % params_dict

    # post_dict["_xsrf"] = "dacc17fefe1dd92f1f814fb77d3a359f"
    post_dict["_xsrf"] = get_xsrf_from_cookie(cookie)
    # print "\n\n...xsrf:%s" % post_dict["_xsrf"]

    post_data = urlencode(post_dict)
    # post_data = 'method=next&params=%7B%22topic_id%22%3A253%2C%22offset%22%3A40%2C%22hash_id%22%3A%22dced108689287057f5cc3b5e85cb8289%22%7D&_xsrf=dacc17fefe1dd92f1f814fb77d3a359f'
    print "... post_data:%s" % post_data

    req = urllib2.Request(toUrl, post_data, headers)
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