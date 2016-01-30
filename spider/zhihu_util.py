#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
from urllib import urlencode
import gzip
import StringIO
import ConfigParser

def get_content(toUrl):
    """ Return the content of given url

        Args:
            toUrl: target url
        Return:
            content if success
            'Fail' if fail
    """

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

def post(toUrl, offset=20):
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

    # method:next
    # params:{"topic_id":253,"offset":40,"hash_id":"dced108689287057f5cc3b5e85cb8289"}
    postDict = {
        "method"  : "next",
        "params"  : '{"topic_id":253,"offset":40,"hash_id":"dced108689287057f5cc3b5e85cb8289"}',
        "_xsrf"   : "dacc17fefe1dd92f1f814fb77d3a359f"
    }
    postData = urlencode(postDict)
    # postData = 'method=next&params=%7B%22topic_id%22%3A253%2C%22offset%22%3A40%2C%22hash_id%22%3A%22dced108689287057f5cc3b5e85cb8289%22%7D&_xsrf=dacc17fefe1dd92f1f814fb77d3a359f'
    print "... postData:%s" % postData

    req = urllib2.Request(toUrl, postData, headers)
    resp = urllib2.urlopen(req)
    content = resp.read()
    if resp.info().get('Content-Encoding') == 'gzip':
        data = StringIO.StringIO(content)
        gz = gzip.GzipFile(fileobj=data)
        content = gz.read()
        gz.close()

    return content