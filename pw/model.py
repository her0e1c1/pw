# -*- coding: utf-8 -*-
import types

import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .encrypt import encrypt, decrypt


def autocommit(delete=False):
    def wrapper(f):
        def wrap(*args, **kw):
            session = Base.session

            objects = f(*args, **kw)
            if not objects:
                return objects

            if delete:
                add_or_delete = getattr(session, "delete")
            else:
                add_or_delete = getattr(session, "add")

            if isinstance(objects, (types.GeneratorType, list)):
                for obj in objects:
                    add_or_delete(obj)
            else:
                add_or_delete(objects)
            session.commit()
            return objects
        return wrap
    return wrapper


class AccountManager(object):

    def __getattribute__(self, name):
        meth = getattr(AccountManager, name, None)
        if meth is not None:
            return meth
        query = AccountManager.query()
        return getattr(query, name)

    @classmethod
    def query(cls):
        return Base.session.query(Account)

    @classmethod
    def exists(cls, id=None, raw_account=None):
        for a in cls.query():
            if a.id == id:
                return True
            elif a.raw_account == raw_account:
                return True
        else:
            return False

    @classmethod
    def create(cls, raw_account, raw_password, description=None):
        if cls.exists(raw_account=raw_account):
            raise ValueError(u"%s already exists" % raw_account)

        a = Account(description=description)
        a.raw_account = raw_account
        a.raw_password = raw_password
        return a

    @classmethod
    def get_by_id_or_account(cls, id_or_account):
        query = cls.query()
        a = query.filter_by(id=id_or_account).first()
        if a:
            return a
        account = encrypt(id_or_account)
        a = query.filter_by(account=account).first()
        return a

Base = declarative_base()


class Account(Base):
    __tablename__ = "account"

    id = sql.Column(sql.Integer, primary_key=True)
    account = sql.Column(sql.BLOB, nullable=True)
    password = sql.Column(sql.BLOB, nullable=False)
    description = sql.Column(sql.Unicode, nullable=True)

    query = AccountManager()

    @property
    def raw_account(self):
        return decrypt(self.account).strip()

    @raw_account.setter
    def raw_account(self, val):
        self.account = encrypt(val)

    @property
    def raw_password(self):
        return decrypt(self.password).strip()

    @raw_password.setter
    def raw_password(self, val):
        self.password = encrypt(val)

    def change_master_key(self, master_key):
        self.account = encrypt(self.raw_account, master_key)
        self.password = encrypt(self.raw_password, master_key)
        return self

    def update(self, raw_account=None, raw_password=None, description=None):
        if raw_account is not None:
            self.account = encrypt(raw_account)

        if raw_password is not None:
            self.password = encrypt(raw_password)

        if description is not None:
            self.description = self.description

        return self


def make_session():
    from .loader import config
    url = config.get("url")
    engine = sql.create_engine(url)
    Account.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

Base.session = make_session()
