#! /usr/bin/env python
# -*- coding: utf-8 -*-


import MySQLdb
import ConfigParser
from zhihu_constants import *


class ZhihuObject:
    def __init__(self, run_mode='prod'):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(CONFIG_INI_PATH)
        
        host = self.cf.get("db", "host")
        port = int(self.cf.get("db", "port"))
        user = self.cf.get("db", "user")
        passwd = self.cf.get("db", "passwd")
        db_name = self.cf.get("db", "db")
        charset = self.cf.get("db", "charset")
        use_unicode = self.cf.get("db", "use_unicode")

        self.db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db_name, charset=charset, use_unicode=use_unicode)
        self.cursor = self.db.cursor()
        self.mode = run_mode

    def is_develop_mode(self):
        return self.mode == 'develop'
