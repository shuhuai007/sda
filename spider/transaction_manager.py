#! /usr/bin/env python
# -*- coding:utf-8 -*-

from _mysql_exceptions import IntegrityError
from connection_pool import ConnectionPool

class TransactionManager(object):
    '''
    handles all transaction and db query
    '''
    def __init__(self):
        self.conn = ConnectionPool().pool.connection()
        self.cursor = self.conn.cursor()

    def startTransaction(self):
        '''
        For databases that support transactions,
        the Python interface silently starts a transaction when the cursor is created.
        so we do nothing here.
        '''
        pass
    def commitTransaction(self):
        self.cursor.close()
        self.conn.commit()

    def endTransaction(self):
        '''
        结束事务
        '''
        pass
    def rollbackTransaction(self):
        '''
        回滚事务
        '''
        self.cursor.close()
        self.conn.rollback()

    def queryInsert(self, sqlid, inputObject):
        '''
        查询插入
        '''
        #=======================================================================
        # resultclasstype参数在没有返回值的时候用不到
        #=======================================================================
        sql, resultclasstype = processSql(sqlid, inputObject)
        try:
            var = self.cursor.execute(sql)
            return var
        except IntegrityError:
            return -1

    def queryUpdate(self, sqlid, inputObject):
        '''
        查询更新
        '''
        self.queryInsert(sqlid, inputObject)
    def queryDelete(self, sqlid, inputObject):
        '''
        查询删除
        '''
        self.queryInsert(sqlid, inputObject)

    def queryForObject(self, sqlid, inputObject):
        '''
        查询并返回一个对象
        '''
        sql, resultclasstype = processSql(sqlid, inputObject)
        self.cursor.execute(sql)
        objList = Data2Object.data2object(self.cursor, resultclasstype)
        if len(objList) == 0:
            return None
        elif len(objList) == 1:
            return objList[0]
        else:
            raise Exception('query for one object, but get many.');

    def queryForList(self, sqlid, inputObject):
        '''
        查询并返回一个列表
        '''
        sql , resultclasstype = self.processSql(sqlid, inputObject)
        self.cursor.execute(sql)
        objList = self.data2object(self.cursor, resultclasstype)
        return objList

    def processSql(self, sqlid, inputObject):
        # TODO (zj)
        return '', ''

    def data2object(cursor, resultclasstype):
        # TODO (zj)
        return []

    def execute_sql(self, sql, pre_sql=None):
        r = []
        try:
            if pre_sql:
                self.cursor.execute(pre_sql)
            self.cursor.execute(sql)
            r = self.cursor.fetchall()
            self.conn.commit()
        except Exception, e:
            print "...exception, rollback"
            self.conn.rollback()
        finally:
            self.cursor.close()
            self.conn.close()
        return r

    def execute_many_sql(self, query, args, pre_sql=None):
        r = []
        try:
            if pre_sql:
                self.cursor.execut(pre_sql)
            self.cursor.executemany(query, args)
            r = self.cursor.fetchall()
            self.conn.commit()
        except Exception, e:
            print "Exception when execute_many_sql:%s, rollback" % e
            self.conn.rollback()
        finally:
            self.cursor.close()
            self.conn.close()
        return r