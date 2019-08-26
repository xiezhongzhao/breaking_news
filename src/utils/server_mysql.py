# -*- coding: utf-8 -*-
from mysql.connector.pooling import MySQLConnectionPool
import logging
import sys

logger = logging.getLogger(__name__)

class ServerMysql(object):

    def __init__(self, config, pool_size=30):
        self._database = {
            'host': config.get('host'),
            'port': config.get('port'),
            'user': config.get('user'),
            'password': config.get('password'),
            'database': config.get('database'),
        }
        self._pool = MySQLConnectionPool(pool_name=None, pool_size=pool_size, **self._database)

    def count_topic(self, table, topic):
        '''
        统计主题的条数
        :param table:
        :return:
        '''
        sql = 'select count(*) from {0} where title = "{1}"'.format(table, topic)
        try:
            conn = self._pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            res = cursor.fetchall()  # [(1000,)]
            res =  res[0][0]
        except BaseException:
            logging.exception('数据库操作错误！')
        finally:
            if conn is not None:
                conn.close()
        return res

    def read_topic_field(self, table, topic, field, rnk):

        sql = 'select {0} from {1} where title = "{2}" and id = {3}'.format(field, table, topic, rnk)
        try:
            conn = self._pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            res = cursor.fetchall()  # [(1000,)]
            res = res[0][0]
        except BaseException:
            logging.exception('数据库操作错误！')
        finally:
            if conn is not None:
                conn.close()
        return res

    def get_fields(self, table, auto_key=None):
        """获取表字段"""
        sql = 'select column_name from information_schema.columns ' \
              'where table_name = "{0}" order ' \
              'by ordinal_position'.format(table)
        conn = None
        res = None
        try:
            conn = self._pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            res = cursor.fetchall()  # [(col1,), (col2,)]
            res = [r[0] for r in res if r[0] != auto_key]
        except BaseException:
            logging.exception('数据库操作错误！')
        finally:
            if conn is not None:
                conn.close()
            return res

    def count_data(self, table):
        """统计记录数"""
        sql = 'select count(*) from {0}'.format(table)
        conn = None
        res = None
        try:
            conn = self._pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            res = cursor.fetchall()  # [(1000,)]
            res =  res[0][0]
        except BaseException:
            logging.exception('数据库操作错误！')
        finally:
            if conn is not None:
                conn.close()
            return res

    def read_data(self, table, fields=None, auto_key=None, batch_size=200, cursor_from=0, cursor_to=None, condition=None):
        """读取表记录"""
        fields = self.get_fields(table, auto_key) if fields is None else fields
        condition = '1 = 1' if condition is None else condition
        sql = 'select {0} from {1}'.format(', '.join(fields), table)
        conn = None
        try:
            conn = self._pool.get_connection()
            cursor = conn.cursor()
            start = cursor_from
            end = self.count_data(table) if cursor_to is None else cursor_to
            if auto_key is None:
                cursor_sql = lambda offset, batch: sql + ' where {2} limit {0}, {1}'.format(offset, batch, condition)  # 用limit全表扫描，随offset增加速度变慢
            else:
                cursor_sql = lambda offset, batch: sql + ' where {0}>{1} and {0}<={2} and {3}'.format(auto_key, offset, offset+batch, condition)  # 用自增列索引查询，效率更高
            while start < end:
                tmp_sql = cursor_sql(start, min(batch_size, end - start))
                cursor.execute(tmp_sql)
                tmp_data = cursor.fetchall()
                logger.info('读取记录数：{0}'.format(len(tmp_data)))
                start += batch_size
                yield tmp_data
        except BaseException:
            logging.exception('数据库读取错误！')
            error_type, error_value, trace_back = sys.exc_info()
            print(error_value)
        finally:
            if conn is not None:
                conn.close()
            return

    def write_data(self, data, table, fields=None, auto_key=None, batch_size=200):
        """写入表记录"""
        fields = self.get_fields(table, auto_key) if fields is None else fields
        sql = 'insert into {0} ({1}) values ({2})'.format(table, ', '.join(fields), ', '.join(['%s'] * len(fields)))
        conn = None
        try:
            conn = self._pool.get_connection()
            cursor = conn.cursor()
            start = 0
            end = len(data)
            while start < end:
                tmp_data = data[start : start+batch_size]
                cursor.executemany(sql, tmp_data)
                start += batch_size
            conn.commit()
            logger.info('写入记录数：{0}'.format(end))
        except BaseException:
            logging.exception('数据库写入错误！')
            error_type, error_value, trace_back = sys.exc_info()
            print(error_value)
        finally:
            if conn is not None:
                conn.close()
            return


if __name__ == '__main__':
    configs = {
        'host': 'localhost',
        'port': '3306',
        'user': 'user',
        'password': '88888888',
        'database': 'webfiles',
    }
    table = 'web_file_test'
    fields = ['col1', 'col2']
    data = [tuple(range(k, k+2)) for k in range(100)]
    handler = ServerMysql(configs)
    handler.write_data(data=data, table=table, batch_size=100)
    print(handler.get_fields(table))
    print(handler.count_data(table))
    for tmp in handler.read_data(table=table, batch_size=10, cursor_from=10, cursor_to=20):
        print(len(tmp))
        print(tmp)

