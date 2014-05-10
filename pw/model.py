# -*- coding: utf-8 -*-
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .encrypt import encrypt, decrypt


def autocommit(delete=False):
    def wrapper(f):
        def wrap(*args, **kw):
            objects = f(*args, **kw)
            if not objects:
                return

            if delete:
                add_or_delete = getattr(session, "delete")
            else:
                add_or_delete = getattr(session, "add")

            if isinstance(objects, list):
                for obj in objects:
                    add_or_delete(obj)
            else:
                add_or_delete(objects)
            session.commit()
        return wrap
    return wrapper


class AccountManager(object):

    def __getattribute__(self, name):
        query = AccountManager.query()
        f = getattr(query, name, None)
        if f is not None:
            return f
        else:
            return getattr(AccountManager, name)

    @classmethod
    def query(cls):
        return session.query(Account)

    @classmethod
    def exists(cls, id=None, account=None):
        for a in cls.query():
            if a.id == id:
                return True
            if a.raw_account == account:
                return True
        else:
            return False

    @classmethod
    def create(cls, raw_account, raw_password, description=None):
        account = encrypt(raw_account)
        password = encrypt(raw_password)
        a = Account(account=account, password=password, description=description)
        if not cls.exists(account=account):
            return a
        else:
            raise ValueError(u"%s already exists" % account)

    def change_master_key(self, new_aes):
        for a in self.query.all():
            yield a.update(raw_password=a.raw_password)

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

    @property
    def raw_password(self):
        return decrypt(self.password).strip()

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
session = make_session()
