#! /usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/..')
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')

import urllib2
from bs4 import BeautifulSoup

from spider import zhihu_util
from spider.transaction_manager import TransactionManager


PROXY_HOST_1 = "www.youdaili.net"
PROXY_WEBSITE_1 = "http://www.youdaili.net/Daili/guowai/"
PROXY_HOST_2 = "free-proxy-list.net"
PROXY_WEBSITE_2 = "http://free-proxy-list.net/"


def parse_ips_1(ip_link):
    ip_content = send_request(ip_link, PROXY_HOST_1, timeout=10)
    # print "ip content:%s" % ip_content
    try:
        soup = BeautifulSoup(ip_content, "html.parser")
        ips = soup.find("div", attrs={'class': 'cont_font'}).find("p").get_text().encode("utf-8")
        # print "ips:%s" % ips
        ip_list = map(lambda ip: ip.split("@")[0], ips.split("\n"))
        # print "ip_list:%s" % ip_list
        return [(ip,) for ip in ip_list if check_proxy(ip)]
    except Exception, e:
        print "parse ips error:%s" % e.message
        return []

def resolve_1():
    ip_list = []

    content = send_request(PROXY_WEBSITE_1, PROXY_HOST_1, timeout=10)

    soup = BeautifulSoup(content, "html.parser")
    ip_links = soup.find_all("a", attrs={'target': '_blank'})
    # print len(ip_links)
    for ip_link in ip_links:
        ip_link = str(ip_link.get("href"))
        if ip_link.endswith(".html") and "Daili" in ip_link:
            print "begin to parse ip_link:%s" % ip_link
            temp_list = parse_ips_1(ip_link)
            if len(temp_list) > 0:
                ip_list += temp_list
    return ip_list

def resolve_2():
    ip_list = []

    content = send_request(PROXY_WEBSITE_2, PROXY_HOST_2, timeout=10)

    soup = BeautifulSoup(content, "html.parser")
    # print "resolve 2:%s" % soup
    tr_list = soup.find('tbody').find_all('tr')
    for tr_item in tr_list:
        td_list = tr_item.find_all('td')
        if td_list[-2] == 'no':  # https:no
            continue
        ip = td_list[0].get_text()
        port = td_list[1].get_text()
        ip_link = ip + ':' + port
        print "ip:port--%s" % ip_link
        if check_proxy(ip_link):
            ip_list.append(ip_link)

    return ip_list

def fetch_ips():
    return resolve_1() + resolve_2()

def send_request(url, proxy_host, timeout=3):
    headers = {
        'Host': proxy_host,
        'Referer': 'https://www.baidu.com/link?url=yZ8Z5H8yiKkLuxTC0mIBGIv3QFEvwmzu2gnzy-XU07URJkC4guyz6beWtZv8d4fh&wd=&eqid=8c6767b700042f580000000256e0d581',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
        'Accept-Encoding': 'gzip'
    }
    try:
        req = urllib2.Request(url=url, headers=headers)
        resp = urllib2.urlopen(req, timeout=timeout)
        content = zhihu_util.get_content_from_resp(resp)
        return content
    except:
        print "send request error"
        return "FAIL"

def check_proxy(ip_proxy):
    proxy_handler = urllib2.ProxyHandler({
        'http': ip_proxy,
        'https': ip_proxy
    })
    opener = urllib2.build_opener(proxy_handler)
    # urllib2.install_opener(opener)

    headers = zhihu_util.get_headers()

    req = urllib2.Request(
        url="https://www.zhihu.com/question/40299633",
        headers=headers
    )
    try:
        resp = opener.open(req, timeout=5)
        content = zhihu_util.get_content_from_resp(resp)
        print "check proxy %s:%s" % (ip_proxy, content != 'FAIL')
        return content != 'FAIL'
    except:
        print "check proxy %s:%s" % (ip_proxy, False)
        return False

def persist(available_ip_list):
    insert_sql = "INSERT IGNORE INTO ZHIHU_PROXY (PROXY_IP) \
                  VALUES (%s)"
    print "insert sql:%s" % insert_sql
    tm = TransactionManager()
    tm.execute_many_sql(insert_sql, available_ip_list)
    tm.close_connection()

def empty_table():
    truncate_sql = "truncate TABLE ZHIHU_PROXY"
    tm = TransactionManager()
    tm.execute_sql(truncate_sql)
    tm.close_connection()


if __name__ == "__main__":
    available_ips = fetch_ips()
    empty_table()
    persist(available_ips)
    # print check_proxy("210.101.131.232:8080")
