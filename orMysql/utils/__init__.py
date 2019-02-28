# coding=utf-8


class Property(object):
    """一个简单的non-data描述器"""
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, obj_type):
        return self.fget(obj_type)


def wrapper_str(s, quotation='"'):
    """包装字符串
    >>> wrapper_str(1, "'")
    "'1'"
    >>> wrapper_str("a", "`")
    '`a`'
    """
    return quotation + str(s) + quotation


if __name__ == "__main__":
    import doctest
    doctest.testmod()