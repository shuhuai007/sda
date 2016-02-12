#!/usr/bin/env python
# encoding: utf-8

import MySQLdb
from DBUtils.PooledDB import PooledDB
import ConfigParser
from zhihu_constants import *


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class ConnectionPool(Singleton):
    def __init__(self):
        cf = ConfigParser.ConfigParser()
        cf.read(CONFIG_INI_PATH)

        host = cf.get("db", "host")
        port = int(cf.get("db", "port"))
        user = cf.get("db", "user")
        passwd = cf.get("db", "passwd")
        db_name = cf.get("db", "db")
        charset = cf.get("db", "charset")
        use_unicode = cf.get("db", "use_unicode")

        self.pool = PooledDB(MySQLdb, 5, host=host, port=port, user=user, passwd=passwd, db=db_name,
                             charset=charset, use_unicode=use_unicode)

if __name__ == '__main__':
    one = ConnectionPool()
    two = ConnectionPool()

    two.a = 3
    print one.a
    #3
    print id(one)
    #29660784
    print id(two)