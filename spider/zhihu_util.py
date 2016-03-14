#! /usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/..')
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../..')

import getopt
import urllib2
import gzip
import StringIO
import ConfigParser
import time
from contextlib import contextmanager
from bs4 import BeautifulSoup

from zhihu_constants import *
from transaction_manager import TransactionManager


def get_content(to_url, max_attempts=3):
    headers = get_headers()

    req = urllib2.Request(
        url=to_url,
        headers=headers
    )

    resp = call_url(max_attempts, req, to_url)

    if resp is None:
        return "FAIL"

    return get_content_from_resp(resp)

PROXY_HOST = "www.youdaili.net"
PROXY_WEBSITE = "http://www.youdaili.net/Daili/guowai/"


def get_proxy_from_db():
    select_sql = "SELECT PROXY_IP FROM ZHIHU_PROXY ORDER BY RAND() LIMIT 1"
    tm = TransactionManager()
    results = tm.execute_sql(select_sql)
    tm.close_connection()
    if len(results) == 0:
        return ""
    for row in results:
        return str(row[0])

def install_opener(proxy_ip):
    if proxy_ip == "":
        proxy_handler = urllib2.ProxyHandler({})
    else:
        proxy_handler = urllib2.ProxyHandler({
            'http': proxy_ip,
            'https': proxy_ip
        })
    opener = urllib2.build_opener(proxy_handler)
    urllib2.install_opener(opener)

@contextmanager
def no_proxies():
    orig_getproxies = urllib2.getproxies
    urllib2.getproxies = lambda: {}
    yield
    urllib2.getproxies = orig_getproxies

def call_url(max_attempts, req, to_url, timeout=5):
    retry = 0
    resp = None
    while resp is None and retry < max_attempts:
        try:
            if retry == (max_attempts - 1):
                proxy_ip = ""
            else:
                proxy_ip = get_proxy_from_db()
            print "proxy_ip:%s" % proxy_ip

            install_opener(proxy_ip)
            resp = urllib2.urlopen(req, timeout=timeout)
            # resp = opener.open(req, timeout=timeout)

        except Exception, e:
            retry += 1
            print "Calling url: {0}, error:{1}, Re-trying.....".format(to_url, e.message)
            time.sleep(1)
    return resp

def post(to_url, post_data, max_attempts=3):
    headers = get_headers()

    req = urllib2.Request(to_url, post_data, headers)
    resp = call_url(max_attempts, req, to_url)

    if resp is None:
        return "FAIL"

    return get_content_from_resp(resp)

def get_content_from_resp(resp):
    try:
        content = resp.read()
        if resp.info().get('Content-Encoding') == 'gzip':
            data = StringIO.StringIO(content)
            gz = gzip.GzipFile(fileobj=data)
            content = gz.read()
            gz.close()
        return content
    except Exception, e:
        print "Error when get_content_from_resp, error message:%s" % e.message
        return "FAIL"

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
    cf.read(CONFIG_INI_PATH)
    cookie = cf.get("cookie", "cookie")
    return cookie

def get_headers():
    cookie = get_cookie()
    headers = {
        'Cookie': cookie,
        'Host': 'www.zhihu.com',
        'Referer': 'www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Accept-Encoding': 'gzip'
    }
    return headers

def parse_options():
    def usage():
        print "Usage:"
        print "-h,--help: print help message."
        print "-m, --mode: develop or prod, prod is default value if not set."
        print "-d, --date: last_visit_date, default value is today's date if not set"

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hm:d:', ['help', 'mode=', 'date='])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    mode = "prod"
    last_visit_date = get_today_date()
    print "...last_visit:%s, opts:%s" % (last_visit_date, opts)
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(1)
        elif opt in ('-m', '--mode'):
            mode = val
        elif opt in ('-d', '--date'):
            last_visit_date = val
        else:
            print 'unhandled option'
            sys.exit(2)
    return mode, last_visit_date

def error_2_file(msg, file_name):
    file_object = open(file_name, 'w+')
    try:
        file_object.write(msg)
    finally:
        file_object.close()

def get_today_date():
    import time

    return time.strftime("%Y-%m-%d")

def get_current_timestamp():
    from datetime import datetime

    i = datetime.now()
    return i.strftime('%Y-%m-%d %H:%M:%S')

import Queue
import sys
from threading import Thread

# working thread
class Worker(Thread):

    worker_count = 0
    timeout = 2

    def __init__(self, work_queue, result_queue, **kwargs):
        Thread.__init__(self, **kwargs)
        self.id = Worker.worker_count
        Worker.worker_count += 1
        self.setDaemon(True)
        self.workQueue = work_queue
        self.resultQueue = result_queue
        self.start()

    def run(self):
        """ the get-some-work, do-some-work main loop of worker threads """
        while True:
            try:
                callable, args, kwds = self.workQueue.get(timeout=Worker.timeout)
                res = callable(*args, **kwds)
                print "worker[%d]'s result: %s" % (self.id, str(res))
                self.resultQueue.put(res)
                # time.sleep(Worker.sleep)
            except Queue.Empty:
                break
            except:
                print "worker[%2d]" % self.id, sys.exc_info()[:2]
                raise


class WorkerManager:

    def __init__(self, num_of_workers=10, timeout=2):
        self.workQueue = Queue.Queue()
        self.resultQueue = Queue.Queue()
        self.workers = []
        self.timeout = timeout
        self._recruit_threads(num_of_workers)

    def _recruit_threads(self, num_of_workers):
        for i in range(num_of_workers):
            worker = Worker(self.workQueue, self.resultQueue)
            self.workers.append(worker)

    def wait_for_complete(self):
        # ...then, wait for each of them to terminate:
        while len(self.workers):
            worker = self.workers.pop()
            worker.join()
            if worker.isAlive() and not self.workQueue.empty():
                self.workers.append(worker)
        print "All jobs are are completed."

    def add_job(self, callable, *args, **kwargs):
        self.workQueue.put((callable, args, kwargs))

    def get_result(self, *args, **kwargs):
        return self.resultQueue.get(*args, **kwargs)


def get_question_data_directory():
    return get_data_directory("question")

def get_answer_data_directory():
    return get_data_directory("answer")

def get_data_directory(keyword):
    import os
    import stat
    data_dir = os.path.abspath(os.path.dirname(__file__)) \
        + "/../data/zhihu/{0}".format(keyword)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        os.chmod(data_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    return os.path.realpath(data_dir)

def get_local_ip():
    import socket

    host_name = socket.getfqdn(socket.gethostname())
    address = socket.gethostbyname(host_name)
    print "...local address:%s" % address
    return address

def get_topic_id_seed(ip):
    cf = ConfigParser.ConfigParser()
    cf.read(CONFIG_INI_PATH)
    try:

        topic_id_seed = cf.get("nodes", ip)
    except:
        topic_id_seed = 1
    return topic_id_seed

def generate_available_topic_ids(max_id, step):
    id_list = []
    # find the seed from config.ini
    topic_id_seed = get_topic_id_seed(get_local_ip())
    print "...............topic_id_seed:%s" % topic_id_seed
    # generate topic id each 10 steps. For example: 1, 11, 21, 31, 41, 51, ...
    topic_id = int(topic_id_seed)
    while topic_id <= max_id:
        id_list.append(str(topic_id))
        topic_id += step

    return ",".join(id_list)

def generate_id_list(id_seed=1, step_range=1, max_id=100):
    id_list = []
    while id_seed <= max_id:
        id_list.append(str(id_seed))
        id_seed += step_range
    return id_list

def get_question_detail_thread_amount():
    question_detail_thread_amount = get_thread_amount("question_detail_thread_amount")
    return question_detail_thread_amount

def get_thread_amount(config_key):
    cf = ConfigParser.ConfigParser()
    cf.read(CONFIG_INI_PATH)
    thread_amount = int(cf.get(config_key, config_key))
    return thread_amount

def write_buffer_file(buffer_list, file_name, delimiter=","):
    if len(buffer_list) == 0:
        return

    with open(file_name, 'a') as target:
        for item_tuple in buffer_list:
            item_list = list(item_tuple)
            item_str = delimiter.join(map(str, item_list))
            target.write(item_str)
            target.write('\n')

def get_file_list(dir_path):
    return [dir_path + '/' + file_name for file_name in os.listdir(dir_path)]

def get_file_names(dir_path):
    return os.listdir(dir_path)

def get_soup(content):
    parser_name = "html.parser" if sys.version_info >= (2, 7) else "html5lib"
    soup = BeautifulSoup(content, parser_name)
    return soup


if __name__ == '__main__':
    # print "...question data dir:%s" % get_question_data_directory()
    # print "get_file_list:%s" % get_file_list("/Users/jiezhou/OpenSource/sda/spider/entity")
    # print "get_file_names:%s" % get_file_names("/Users/jiezhou/OpenSource/sda/spider/entity")
    print str(get_current_timestamp())
    import zhihu_question
    zhihu_question.update_level2_topic_timestamp('19551292')
