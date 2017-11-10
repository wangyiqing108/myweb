#encoding: utf-8

import MySQLdb

import gconf

class MySQLConnection(object):


    def __init__(self, host, port, user, passwd, db, charset='utf8'):
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__db = db
        self.__charset = charset
        self.__conn = None
        self.__cur = None
        self.__connect()

    def __connect(self):
        try:
            self.__conn = MySQLdb.connect(host=self.__host, port=self.__port, \
                            user=self.__user, passwd=self.__passwd, \
                            db=self.__db, charset=self.__charset)
            self.__cur = self.__conn.cursor()
        except BaseException as e:
            print e

    def execute(self, sql, args=()):
        _cnt = 0
        if self.__cur:
            _cnt = self.__cur.execute(sql, args)
        return _cnt

    def fetch(self, sql, args=()):
        _cnt = 0
        _rt_list = []
        #_cnt =self.execute(sql, args)
        if self.__cur:
            _cnt = self.__cur.execute(sql, args)
            _rt_list = self.__cur.fetchall()
        return _cnt, _rt_list

    def commit(self):
        if self.__conn:
            self.__conn.commit()

    def close(self):
        self.commit()
        if self.__cur:
            self.__cur.close()
            self.__cur = None

        if self.__conn:
            self.__conn.close()
            self.__conn = None

    @classmethod
    def execute_sql(cls, sql, args=(), fetch=True):
        _count = 0
        _rt_list = []

        _conn = MySQLConnection(host=gconf.MYSQL_HOST, port=gconf.MYSQL_PORT, \
                            user=gconf.MYSQL_USER, passwd=gconf.MYSQL_PASSWD, \
                            db=gconf.MYSQL_DB, charset=gconf.MYSQL_CHARSET)
        if fetch:
            _count, _rt_list = _conn.fetch(sql, args)
        else:
            _count = _conn.execute(sql, args)
        _conn.close()
        return _count, _rt_list

    @classmethod
    def bulker_execute_sql(cls, sql, args_list=[]):
        _count = 0
        _rt_list = []
        _conn = MySQLConnection(host=gconf.MYSQL_HOST, port=gconf.MYSQL_PORT, \
                            user=gconf.MYSQL_USER, passwd=gconf.MYSQL_PASSWD, \
                            db=gconf.MYSQL_DB, charset=gconf.MYSQL_CHARSET)

        for _args in args_list:
            _count += _conn.execute(sql, _args)
        _conn.close()
        return _count, _rt_list

if __name__ == '__main__':
    print MySQLConnection.execute_sql('select * from user')

