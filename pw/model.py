# -*- coding: utf-8 -*-
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .encrypt import encrypt, decrypt


def make_session():
    from .loader import config
    url = config.get("url")
    engine = sql.create_engine(url)
    Account.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def autocommit(func):
    def wrap(*args, **kw):
        session = make_session()
        objects = func(*args, **kw)
        if not objects:
            return

        if isinstance(objects, list):
            for obj in objects:
                session.add(obj)
        else:
            session.add(objects)
        session.commit()
    return wrap


class AccountManager(type):

    @classmethod
    def query(cls):
        cls.session = make_session()
        return cls.session.query(Account)

    @classmethod
    def delete(cls, id, account=None):
        query = cls.query().filter_by(id=id)
        if query.first():
            query.delete()
            cls.session.commit()
        else:
            print("id %s does not exist." % id)

    @classmethod
    def all(cls):
        return cls.query().all()

    @classmethod
    def first(cls, **kw):
        account = kw.get("account")
        if account:
            kw["account"] = encrypt(account)

        return cls.query().filter_by(**kw).first()

    @classmethod
    def delete_all(cls):
        cls.query().delete()
        cls.session.commit()

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
            cls.session.add(a)
            cls.session.commit()
        else:
            raise ValueError(u"%s already exists" % account)

    def change_master_key(self, new_aes):
        for a in self.query.all():
            a.update(raw_password=a.raw_password)
            self.session.add(a)


Base = declarative_base()
class Account(Base):
    __tablename__ = "account"

    id = sql.Column(sql.Integer, primary_key=True)
    account = sql.Column(sql.BLOB, nullable=True)
    password = sql.Column(sql.BLOB, nullable=False)
    description = sql.Column(sql.Unicode, nullable=True)
    query = AccountManager

    @property
    def raw_account(self):
        return decrypt(self.account).strip()

    @property
    def raw_password(self):
        return decrypt(self.password).strip()

    def change_master_key(self, master_key):
        self.account = encrypt(self.raw_account, master_key)
        self.password = encrypt(self.raw_password, master_key)
        self.save()

    def update(self, raw_account=None, raw_password=None, description=None):
        if raw_account is not None:
            self.account = encrypt(raw_account)

        if raw_password is not None:
            self.password = encrypt(raw_password)

        if description is not None:
            self.description = self.description
        self.save()

    def save(self):
        self.query.session.add(self)
        self.query.session.commit()
