# coding=utf-8

from __future__ import unicode_literals

import unittest
from datetime import datetime, timedelta

import sys

import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orMysql.db import db
from orMysql.fields import IntFiled, StringFiled, DateTimeFiled
from orMysql.model import Model


class User(Model):
    __tablename__ = "tt.user"
    id_ = IntFiled(name="id", primary_key=True)
    name = StringFiled(name="name")
    create_time = DateTimeFiled(name="create_time")


class TestOrm(unittest.TestCase):
    def tearDown(self):
        db.session.do_execute("delete from tt.user")

    def test_orm(self):
        user = User(id_=1, name="linghaihui", create_time=datetime.now())
        result = db.session.add(user)
        self.assertEqual(result, 1)

        result = User.query.all()
        self.assertEqual(len(result), 1)

        result = User.get(1)

        assert isinstance(result, User)

        try:
            result = User.query.filter(User.id_ == 2).first()
        except Exception as e:
            self.assertEqual(e.message, "record not exist")

        result = User.query.filter(User.id_ == 1).first()
        self.assertTrue(isinstance(result, User))

        result = User.query.filter(User.id_ > 1).all()
        assert len(result) == 0

        result = User.query.filter(User.id_ < 1).all()
        assert len(result) == 0

        result = User.query.filter(User.id_ >= 1).all()
        assert len(result) == 1

        result = User.query.filter(User.id_ <= 1).all()
        assert len(result) == 1

        result = User.query.filter(User.name == "linghaihui").all()
        assert len(result) == 1

        result = User.query.filter(User.name.like("ling%")).all()
        assert len(result) == 1

        result = User.query.filter(User.name.like("%ling")).all()
        assert len(result) == 0

        result = User.query.limit(1).all()
        assert len(result) == 1

        user2 = User(id_=2, name="another people", create_time=datetime.now() - timedelta(days=1))

        result = db.session.add(user2)

        assert result == 1

        result = User.query.order_by(User.id_.desc()).limit(1).all()
        assert len(result) == 1 and result[0].id_ == 2

        result = User.query.order_by(User.create_time.desc(), User.name.asc()).all()

        assert len(result) == 2 and result[0].id_ == 1

        result = db.session.update(user2, name="linghaihui", id_=3)
        assert result == 1

        result = User.query.filter(User.name == "linghaihui").order_by(User.id_.desc()).all()

        assert len(result) == 2 and result[0].id_ == 3

        print "unit test done !!!"


class TestPool(unittest.TestCase):

    def tearDown(self):
        db.session.do_execute("delete from tt.user")

    def add(cls):
        db.session.add(User(name="haihui", create_time=datetime.now()))

    def update(cls, user):
        db.session.update(user, name="haihui")

    def get(cls, id_):
        obj = User.query.filter(User.id_==id_).first()
        return obj

    def test_add(self):
        import threading
        try_times = 100
        while try_times > 0:
            threads = []
            for x in range(20):
                threads.append(threading.Thread(target=self.add, args=()))
            for x in threads:
                x.start()
            for x in threads:
                x.join()
            try_times -= 1
        print "test_add done !!!"

    def test_update(self):
        import threading
        try_times = 100
        user = User(id_=1, name="haihui")
        db.session.add(user)
        while try_times > 0:
            threads = []
            for x in range(20):
                threads.append(threading.Thread(target=self.update, args=(user, )))
            for x in threads:
                x.start()
            for x in threads:
                x.join()
            try_times -= 1
        print "test_update done !!!"

    def test_get(self):
        import threading
        try_times = 100
        user = User(id_=1, name="haihui")
        db.session.add(user)
        while try_times > 0:
            threads = []
            for x in range(20):
                threads.append(threading.Thread(target=self.get, args=(1, )))
            for x in threads:
                x.start()
            for x in threads:
                x.join()
            try_times -= 1
        print "test_get done !!!"


if __name__ == "__main__":
    unittest.main()
