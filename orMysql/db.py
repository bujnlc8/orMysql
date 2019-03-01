# coding=utf-8

from __future__ import unicode_literals

import os
import warnings
from Queue import Queue, Empty
from datetime import datetime, timedelta

from pymysql.connections import Connection
from pymysql.cursors import DictCursor
from utils import Property

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


class PutError(Exception):
    error_no = 5001
    msg = "放回连接池出错"

    def __repr__(self):
        return "error_no:{}, msg:{}".format(self.error_no, self.msg)


class WrapperConnection(Connection):
    def __init__(self, max_life_time=3600, pool=None, **kwargs):
        self.max_life_time = max_life_time
        self.create_time = datetime.now()
        self.end_time = self.create_time + timedelta(seconds=self.max_life_time)
        self.pool = pool
        super(WrapperConnection, self).__init__(**kwargs)

    @property
    def is_dead(self):
        """不检查是否依然保持连接，理论上应该是能保持的"""
        if datetime.now() >= self.end_time:
            return True
        return False

    def __exit__(self, exc, value, traceback):
        try:
            if exc is not None:
                self.rollback()
            self.pool.put(self)
        except PutError as e:
            print e

    def select(self, sql):
        """
        查询接口封装
        :param sql : the sql to execute
        """
        with self as cur:
            cur.execute(sql)
            result = cur.fetchall()
            self.commit()
        return result

    def _inner_execute(self, obj, op="save"):
        """
        仅限内部调用
        """
        with self as cur:
            result = 0
            if op == "save":
                result = cur.execute(obj.save)
            elif op == "update":
                result = cur.execute(obj)
            self.commit()
            return result

    def add(self, obj):
        """
        保存对象接口封装
        :param obj: the model object to save
        """
        return self._inner_execute(obj)

    def update(self, sql):
        """
        :param sql: the sql to update
        """
        return self._inner_execute(sql, op="update")

    def do_execute(self, sql):
        with self as cur:
            result = cur.execute(sql)
            self.commit()
        return result


class Pool(object):
    """
    一个基于pymysql的连接池
    :param pool_max_size:  连接池最大的容量， 默认为5
    :param max_life_time:  连接最大的存活时间，以秒为单位，默认是3600，如果超过了时间自动断开
    :param try_times: 获取连接最大的尝试次数 默认是三次
    """

    def __init__(self, host="127.0.0.1", port=3306, user="root",
                 password="", db="", charset="utf8mb4",
                 pool_max_size=5, max_life_time=3600, try_times=3):
        self.pool = Queue(maxsize=pool_max_size)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset
        self.pool_max_size = pool_max_size
        self.max_life_time = max_life_time
        if try_times <= 0:
            try_times = 2
        self.try_times = try_times

    @property
    def connection(self):
        """
        基本的算法是先从pool里面去取连接，如果取到，判断有没有超时， 
        如果超时，重新获取，否则返回。如果没取到，重新连接数据库获取连接
        """
        try_times = self.try_times
        try:
            while try_times > 0:
                con = self.pool.get(block=False)
                if not con.is_dead:
                    return con
                try_times -= 1
        except Empty as e:
            try:
                while try_times > 0:
                    con = WrapperConnection(
                        host=self.host,
                        user=self.user,
                        password=self.password,
                        db=self.db,
                        port=self.port,
                        charset=self.charset,
                        max_life_time=self.max_life_time,
                        cursorclass=DictCursor, pool=self)
                    return con
            except Exception as e:
                try_times -= 1
        return None

    def put(self, connection):
        try:
            if not connection.is_dead:
                self.pool.put_nowait(connection)
            else:
                # 尝试断开连接
                connection.close()
        except Exception as e:
            raise PutError

    @property
    def session(self):
        con = self.connection
        if not con:
            raise Exception('get connection failed, connection args error ?')
        return con


MYSQL_CONNECTION_ARGS = {"OR_MYSQL_HOST": str,
                         "OR_MYSQL_PORT": int,
                         "OR_MYSQL_USER": str,
                         "OR_MYSQL_PASSWORD": str,
                         "OR_MYSQL_DB": str,
                         "OR_MYSQL_CHARSET": str,
                         "OR_MYSQL_MAX_POOL_SIZE": int,
                         "OR_MYSQL_MAX_LIFE_TIME": int,
                         "OR_MYSQL_TRY_TIMES": int
                         }

MYSQL_CONNECTION_ARGS_TRANS = {"OR_MYSQL_HOST": "host",
                               "OR_MYSQL_PORT": "port",
                               "OR_MYSQL_USER": "user",
                               "OR_MYSQL_PASSWORD": "password",
                               "OR_MYSQL_DB": "db",
                               "OR_MYSQL_CHARSET": "charset",
                               "OR_MYSQL_MAX_POOL_SIZE": "pool_max_size",
                               "OR_MYSQL_MAX_LIFE_TIME": "max_life_time",
                               "OR_MYSQL_TRY_TIMES": "try_times"
                               }


def get_db():
    """
    获取数据库连接对象，首先从环境变量里获取连接参数，
    如果没有获取到，从本目录下面的env文件中获取
    """
    connect_args = {}
    for name, trans_method in MYSQL_CONNECTION_ARGS.iteritems():
        v = os.environ.get(name)
        if v:
            connect_args[name] = trans_method(v)
    if not connect_args:
        try:
            with open(os.sep.join([BASE_PATH, ".env"]), "r") as f:
                for line in f:
                    if line.startswith("#") or line.startswith("--"):
                        continue
                    strs = line.split("=")
                    if strs[1]:
                        s = strs[1].strip()
                        connect_args[strs[0]] = MYSQL_CONNECTION_ARGS[strs[0]](s)
        except Exception as e:
            msg = "maybe file .env not exist in %s" % BASE_PATH
            warnings.warn(msg, RuntimeWarning)
    trans_connect_args = {}
    for k, v in connect_args.iteritems():
        trans_connect_args[MYSQL_CONNECTION_ARGS_TRANS[k]] = v
    if not trans_connect_args:
        warnings.warn("you need set up the environments to connect to mysql", RuntimeWarning)
        return None
    return Pool(**trans_connect_args)


class Db(object):

    _pool = get_db()

    @Property
    def session(self):
        if not self._pool:
            raise Exception("you need revoke db.setup_db method to setup mysql")
        else:
            pool = self.get_pool()
            return pool.session

    @classmethod
    def get_pool(cls):
        return cls._pool

    @classmethod
    def set_pool(cls, pool):
        cls._pool = pool

    @classmethod
    def setup_db(cls, host="127.0.0.1", port=3306, user="root",
                 password="123456", database="", charset="utf8mb4",
                 pool_max_size=5, max_life_time=3600,
                 try_times=3):
        pool = Pool(host, port, user, password, database, charset,
                       pool_max_size, max_life_time, try_times)
        cls.set_pool(pool)


db = Db