[![Build Status](https://travis-ci.com/linghaihui/orMysql.svg?branch=master)](https://travis-ci.com/linghaihui/orMysql)

#### orMysql, 顾名思义是一个针对mysql的orm,
可以看成[sqlalchemy](https://www.sqlalchemy.org/)的精简版，但是也能满足大部分的需求。
它的mysql客户端使用[PyMySQL](https://github.com/PyMySQL/PyMySQL), orMysql在内部实现了一个连接池，可以回收使用宝贵的连接。
具体像下面这样👇

```python
from orMysql.db import db
from orMysql.model import Model

class User(Model):
    __tablename__ = 'test.user'
    id_ = IntFiled(name="id", doc="用户id", primary_key=True)
    age = IntFiled(name="age", doc="用户年龄")
    name = StringFiled(name="name", doc="用户姓名")

    @classmethod
    def add(cls, age, name):
        user = cls(age=age, name=name)
        db.session.add(user)

    @classmethod
    def get(cls, id):
        return cls.query.filter(cls.id_==id).first()

    def update(self, **kw):
        self.update(**kw)
```

#### 用法说明

在使用之前需要先设置以下环境变量来使用数据库:

```shell
OR_MYSQL_HOST=127.0.0.1   # 数据库host
OR_MYSQL_PORT=33062       # 数据库port
OR_MYSQL_USER=root        # 数据库user
OR_MYSQL_PASSWORD=123456  # 数据库密码
OR_MYSQL_DB=              # 选择的数据库，可以在表中指定
OR_MYSQL_CHARSET=utf8mb4  # 客户端编码
OR_MYSQL_MAX_POOL_SIZE=5  # 连接池大小，默认为5
OR_MYSQL_MAX_LIFE_TIME=3600 # 连接最大存活时间，单位秒
OR_MYSQL_TRY_TIMES=3  # 获取连接尝试的次数i，默认三次
```

如果在环境变量里面没有设置， 可以在代码里调用`orMysql.db.db.setup_db`设置。

具体用法见[测试](https://github.com/linghaihui/orMysql/blob/master/tests/test_orm.py)

本项目可能存在一些坑，欢迎拍砖🧱。

本项目license是`MIT`。具体见[LICENSE](https://github.com/linghaihui/orMysql/blob/master/LICENSE)。
