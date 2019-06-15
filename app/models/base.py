# coding=UTF-8
from contextlib import contextmanager
import datetime

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
from sqlalchemy import Column, SmallInteger, DateTime
from sqlalchemy.sql.elements import BinaryExpression

from app.libs.error_code import NotFound


# 继承_SQLAlchemy，自定义自己的方法
class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


class Query(BaseQuery):
    def filter_by(self, **kwargs):
        if "status" not in kwargs.keys():
            kwargs["status"] = 1
        return super(Query, self).filter_by(**kwargs)

    # def filter(self, *args):
    #     a = args
    #
    #     if "status == 1" not in args:
    #         args = ("status == 1",) + args
    #     return super(Query, self).filter(*args)


    def get_or_404(self, ident, description=None):
        rv = self.get(ident)
        if not rv:
            if description == None:
                raise NotFound()
            else:
                raise NotFound(msg=description)
        return rv

    def first_or_404(self, description=None):
        rv = self.first()
        if not rv:
            if description == None:
                raise NotFound()
            else:
                raise NotFound(msg=description)
        return rv


db = SQLAlchemy(query_class=Query)


class Base(db.Model):
    # # 不创建表，仅仅作为基类
    __abstract__ = True

    create_time = Column(DateTime, default=datetime.datetime.now)  # 创建时间
    status = Column(SmallInteger, default=1)  # 状态，1为可用

    def delete(self):
        # 软删除
        self.status = 0

    # def keys(self):
    #     return self.field
