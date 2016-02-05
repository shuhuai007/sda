import MySQLdb
from DBUtils.PooledDB import PooledDB
from transaction_manager import TransactionManager

if __name__ == '__main__':
    transaction = TransactionManager()
    pre_sql = "SET @index=0;"
    sql = "select @index:=@index+1, question_id from ZHIHU_QUESTION_ID limit 100"

    r = transaction.execute_sql(sql, pre_sql)
    print "...r:%s" % str(r)
