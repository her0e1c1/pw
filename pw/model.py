# -*- coding: utf-8 -*-
from contextlib import contextmanager
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .encrypt import encrypt, decrypt


Base = declarative_base()
class Account(Base):
    __tablename__ = "account"

    id = sql.Column(sql.Integer, primary_key=True)
    account = sql.Column(sql.BLOB, nullable=True)
    password = sql.Column(sql.BLOB, nullable=False)
    description = sql.Column(sql.Unicode, nullable=True)

    @property
    def raw_account(self):
        return decrypt(self.account)

    @property
    def raw_password(self):
        return decrypt(self.password)

    def update(self, raw_account=None, raw_password=None, description=None):
        if raw_account is not None:
            self.account = encrypt(raw_account) 

        if raw_password is not None:
            self.password = encrypt(raw_password)

        if description is not None:
            self.description = self.description

    @classmethod
    def query(cls):
        return session.query(cls)

    @classmethod
    def delete(cls, id, account=None):
        one = cls.query().filter_by(id=id).one()
        return one

    @classmethod
    def delete_all(cls):
        for a in cls.query():
            yield a

    @classmethod
    def change_master_key(self, new_aes):
        for a in cls.query.all():
            a.update(raw_password=a.raw_password)
            yield a

    @classmethod
    def create(cls, raw_account, raw_password, description=None):
        account = encrypt(raw_account)
        password = encrypt(raw_password)
        a = Account(account=account, password=password, description=description)
        if not cls.exists(account=account):
            return a
        else:
            raise ValueError("%s already exists" % account)

    @classmethod
    def exists(cls, id=None, account=None):
        for a in cls.query():
            if a.id == id:
                return True
            if a.account == account:
                return True
        else:
            return False

def search_account(target_account):
    """
    find the encrypted account or the decrypted account by a ``target_account`` key.
    In an either way, return id, **decrypted account**, **decrypted password**.
    """
    for a in Account.query.all():
        id = a.id
        account, password = self.decrypt(a.account, a.password)
        if account == target_account or a.account == target_account:
            return id, account, password


def make_session():
    from .loader import config
    url = config.get("url")
    print url
    engine = sql.create_engine(url)
    Account.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

session = make_session()

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = make_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
