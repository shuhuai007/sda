#!/usr/bin/env python

import threading
from time import ctime

class MyThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.res = None

    def get_result(self):
        return self.res

    def run(self):
        print 'starting', self.name, 'at:', \
            ctime()
        res = apply(self.func, self.args)
        self.res = res
        print self.name, 'finished at:', \
            ctime()
