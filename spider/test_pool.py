#!/usr/bin/env python
# encoding: utf-8

import time
from zhihu_util import *

def myTelnet(i):
    print "this is %s thread" % i
    return


print 'start testing'
wm = WorkerManager(10)

for i in range(1, 5):
    wm.add_job(myTelnet, i)
wm.wait_for_complete()
print 'end testing'
