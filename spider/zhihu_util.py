#! /usr/bin/env python
# -*- coding: utf-8 -*-

import getopt
import urllib2
import gzip
import StringIO
import ConfigParser
import time
from zhihu_constants import *


def get_content(to_url, max_attempts=3):
    headers = get_headers()

    req = urllib2.Request(
        url=to_url,
        headers=headers
    )

    try:
        opener = urllib2.build_opener(urllib2.ProxyHandler())
        urllib2.install_opener(opener)
    except Exception, e:
        print "......urllib2 install opener fail:%s......" % e.message
        return "FAIL"

    resp = call_url(max_attempts, req, to_url)

    if resp is None:
        return "FAIL"

    return get_content_from_resp(resp)


def call_url(max_attempts, req, to_url):
    retry = 0
    resp = None
    while resp is None and retry < max_attempts:
        try:
            resp = urllib2.urlopen(req, timeout=30)
        except Exception, e:
            retry += 1
            print "Calling url: {0}, error:{1}, Re-trying.....".format(to_url, e.message)
            time.sleep(3)
    return resp


def post(to_url, post_data, max_attempts=3):
    headers = get_headers()

    req = urllib2.Request(to_url, post_data, headers)
    resp = call_url(max_attempts, req, to_url)

    if resp is None:
        return "FAIL"

    return get_content_from_resp(resp)


def get_content_from_resp(resp):
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


import Queue, sys
from threading import Thread

# working thread
class Worker(Thread):
    worker_count = 0
    timeout = 2

    def __init__(self, work_queue, result_queue, **kwds):
        Thread.__init__(self, **kwds)
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
        self._recruitThreads(num_of_workers)

    def _recruitThreads(self, num_of_workers):
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

    def add_job(self, callable, *args, **kwds):
        self.workQueue.put((callable, args, kwds))

    def get_result(self, *args, **kwds):
        return self.resultQueue.get(*args, **kwds)


def get_question_data_directory():
    import os
    # TODO (zj) should be constant variable
    question_data_dir = os.path.abspath('../../data/zhihu/question')
    return question_data_dir

def get_answer_data_directory():
    import os
    # TODO (zj) should be constant variable
    answer_data_dir = os.path.abspath('../../data/zhihu/answer')
    if not os.path.exists(answer_data_dir):
        os.mkdir(answer_data_dir, mode=777)
    return answer_data_dir

def get_local_ip():
    import socket

    host_name = socket.getfqdn(socket.gethostname())
    address = socket.gethostbyname(host_name)
    print "...local address:%s" % address
    return address

def get_topic_id_seed(ip):
    cf = ConfigParser.ConfigParser()
    cf.read(CONFIG_INI_PATH)

    topic_id_seed = cf.get("nodes", ip)
    return topic_id_seed

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

    target = open(file_name, 'a')
    for item_tuple in buffer_list:
        item_list = list(item_tuple)
        item_str = delimiter.join(map(str, item_list))
        target.write(item_str)
        target.write('\n')
    target.close()


if __name__ == '__main__':
    print "...question data dir:%s" % get_question_data_directory()
