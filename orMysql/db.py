# coding=utf-8

from __future__ import unicode_literals

import os
import warnings
from Queue import Queue, Empty
from datetime import datetime, timedelta

from pymysql.connections import Connection
from pymysql.cursors import DictCursor

from utils import Property, wrapper_str

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


class WrapperConnection(Connection):
    """
    the wrapper connection of pymysql.connections.Connection
    """
    def __init__(self, max_life_time=3600, pool=None, **kwargs):
        self.max_life_time = max_life_time
        self.create_time = datetime.now()
        self.end_time = self.create_time + timedelta(seconds=self.max_life_time)
        self.pool = pool
        super(WrapperConnection, self).__init__(**kwargs)

    @property
    def is_dead(self):
        """check the connection is over time"""
        if datetime.now() >= self.end_time:
            return True
        return False

    def __exit__(self, exc, value, traceback):
        try:
            if exc is not None:
                self.rollback()
            self.pool.put(self)
        except Exception as e:
            print e

    def select(self, sql):
        """
        :param sql : the sql to execute
        >>> db.session.select(sql)
        """
        with self as cur:
            cur.execute(sql)
            result = cur.fetchall()
            self.commit()
        return result

    def add(self, obj):
        """
        :param obj: the model object to save
        >>> db.session.add(obj)
        """
        attr_map = {}
        for key in obj.keys():
            try:
                attr_map[key] = obj.__map__[key]
            except KeyError as e:
                msg = "{} has no a filed named {}".format(obj.__tablename__, e)
                warnings.warn(msg, SyntaxWarning)
        fileds = []
        values = []
        for k, v in attr_map.iteritems():
            fileds.append(wrapper_str(obj.__map__[k].name, "`"))
            values.append(v.connect_str(obj[k]))
        sql = "INSERT INTO %s (%s) VALUES (%s) " % (
            obj.__tablename__,
            ",".join(fileds),
            ",".join(values))
        return self.do_execute(sql)

    def update(self, obj, **kwargs):
        """
        :param obj: the obj to update
        :param kwargs: the updated attr
        >>> db.session.update(obj, id=100, name="haihui")
        """
        updates = []
        for k, v in kwargs.iteritems():
            if k in obj.__map__:
                updates.append(obj.__map__[k].name + "=" + obj.__map__[k].connect_str(v))
        if not updates:
            return False
        sql = "UPDATE %s SET %s WHERE " % (obj.__tablename__, ",".join(updates))
        # 根据主键设置过滤条件
        wheres = []
        for key in obj.__primary_key__:
            wheres.append(key + "=" + obj.__map__[obj.__db_map__[key]].connect_str(obj[obj.__db_map__[key]]))
        if not wheres:
            return 0
        sql += " AND ".join(wheres)
        return self.do_execute(sql)

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
                # try to close
                connection.close()
        except Exception as e:
            raise Exception("put into pool error happens")

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