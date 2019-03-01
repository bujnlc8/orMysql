[![Build Status](https://travis-ci.com/linghaihui/orMysql.svg?branch=master)](https://travis-ci.com/linghaihui/orMysql)

#### orMysql, 顾名思义是一个针对mysql的orm, 像下面这样👇

```python

class User(Model):
    __tablename__ = 'test.user'
    id_ = IntFiled(name="id", doc="用户id", primary_key=True)
    age = IntFiled(name="age", doc="用户年龄")
    name = StringFiled(name="name", doc="用户姓名")
```
#### 用法说明
在使用之前需要先设置以下环境变量来使用数据库:

```
OR_MYSQL_HOST=127.0.0.1
OR_MYSQL_PORT=33062
OR_MYSQL_USER=root
OR_MYSQL_PASSWORD=123456
OR_MYSQL_DB=
OR_MYSQL_CHARSET=utf8mb4
OR_MYSQL_MAX_POOL_SIZE=5
OR_MYSQL_MAX_LIFE_TIME=3600
OR_MYSQL_TRY_TIMES=3
```
如果在环境变量里面没有设置， 可以在代码里调用`orMysql.db.db.setup_db`设置。

具体用法见[单元测试](https://github.com/linghaihui/orMysql/blob/master/tests/test_orm.py)
