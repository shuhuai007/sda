import MySQLdb
from DBUtils.PooledDB import PooledDB

if __name__ == '__main__':
    pool = PooledDB(MySQLdb, 5, host='localhost', user='root', passwd='root', db='sda', port=3306)

    conn = pool.connection()
    cur = conn.cursor()
    SQL = "select count(*) from ZHIHU_QUESTION"
    r = cur.execute(SQL)
    r = cur.fetchall()
    print "...r:%s" % str(r)
    cur.close()
    conn.close()
