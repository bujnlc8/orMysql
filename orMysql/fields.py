# coding=utf-8

from orMysql.utils import wrapper_str
from datetime import datetime


class BaseField(object):
    """
    字段基类
    :param name: 数据库字段名称
    :param doc: 字段说明
    :param default: 默认值
    :param primary_key: 是否是主键，支持联合主键
    """
    def __init__(self, name="", doc="", default="", primary_key=False):
        self.name = name
        self.doc = ""
        self.default = ""
        self.primary_key = primary_key
    
    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        return self.name + "=" + str(other)
    
    def __ne__(self, other):
        return self.name + "!=" + str(other)

    def __lt__(self, other):
        return self.name + "<" + str(other)

    def __gt__(self, other):
        return self.name + ">" + str(other)
    
    def __le__(self, other):
        return self.name + "<=" + str(other)

    def __ge__(self, other):
        return self.name + ">=" + str(other)
    
    def like(self, s):
        return self.name + " LIKE %s " % wrapper_str(s)
    
    def desc(self):
        return self.name + " DESC "

    def asc(self):
        return self.name + " ASC "
    
    def connect_str(self, v):
        """和字符串连接时样子"""
        return str(v)


class IntFiled(BaseField):
    def __init__(self, name="", doc="", default=0, primary_key=False):
        super(IntFiled, self).__init__(
            name=name, 
            doc=doc, 
            default=default, 
            primary_key=primary_key)


class FloatFiled(BaseField):
    def __init__(self, name="", doc="", default=0, primary_key=False):
        super(FloatFiled, self).__init__(
            name=name,
            doc=doc,
            default=default,
            primary_key=primary_key)


class StringFiled(BaseField):
    def __init__(self, name="", doc="", default="", primary_key=False):
        super(StringFiled, self).__init__(
            name=name, 
            doc=doc, 
            default=default, 
            primary_key=primary_key)
    
    def __eq__(self, other):
        return self.name + "=" + wrapper_str(other)
    
    def __ne__(self, other):
        return self.name + "!=" + wrapper_str(other)

    def __lt__(self, other):
        return self.name + "<" + wrapper_str(other)

    def __gt__(self, other):
        return self.name + ">" + wrapper_str(other)

    def __ge__(self, other):
        return self.name + ">=" + wrapper_str(other)

    def __le__(self, other):
        return self.name + "<=" + wrapper_str(other)
    
    def connect_str(self, v):
        return wrapper_str(v)


class DateTimeFiled(BaseField):
    def __init__(self, name="", doc="", default="", primary_key=False):
        super(DateTimeFiled, self).__init__(
            name=name, doc=doc, 
            default=default, 
            primary_key=primary_key)
    
    def __eq__(self, other):
        if isinstance(other, datetime):
            other = other.strftime("%Y-%m-%d %H:%M:%S")
        return self.name + "=" + wrapper_str(other)
    
    def __ne__(self, other):
        if isinstance(other, datetime):
            other = other.strftime("%Y-%m-%d %H:%M:%S")
        return self.name + "!=" + wrapper_str(other)

    def __lt__(self, other):
        if isinstance(other, datetime):
            other = other.strftime("%Y-%m-%d %H:%M:%S")
        return self.name + "<" + wrapper_str(other)

    def __gt__(self, other):
        if isinstance(other, datetime):
            other = other.strftime("%Y-%m-%d %H:%M:%S")
        return self.name + ">" + wrapper_str(other)
    
    def __le__(self, other):
        if isinstance(other, datetime):
            other = other.strftime("%Y-%m-%d %H:%M:%S")
        return self.name + "<=" + wrapper_str(other)

    def __ge__(self, other):
        if isinstance(other, datetime):
            other = other.strftime("%Y-%m-%d %H:%M:%S")
        return self.name + ">=" + wrapper_str(other)
    
    def connect_str(self, v):
        return wrapper_str(v.strftime("%Y-%m-%d %H:%M:%S"))