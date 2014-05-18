import unittest

import sqlalchemy as sql
import factory
from factory.alchemy import SQLAlchemyModelFactory

from pw.model import Account, Base


class AccountFactory(SQLAlchemyModelFactory):
    FACTORY_FOR = Account
    #FACTORY_SESSION = session

    id = factory.Sequence(lambda n: n)
    description = "THIS IS A DESCRIPTION"

    @factory.lazy_attribute
    def raw_account(self):
        return "account_{id}".format(id=self.id)

    @factory.lazy_attribute
    def raw_password(self):
        return "password_{id}".format(id=self.id)


class BaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = sql.create_engine("sqlite:///:memory:")
        cls.Session = sql.orm.sessionmaker(bind=cls.engine)
        Account.metadata.create_all(cls.engine)

    def setUp(self):
        conn = self.engine.connect()
        self.trans = conn.begin()
        self.session = self.Session(bind=conn)
        Base.session = self.session
        AccountFactory.FACTORY_SESSION = self.session

    def tearDown(self):
        self.trans.rollback()
        self.session.close()

    @classmethod
    def tearDownClass(cls):
        Account.metadata.drop_all(cls.engine)
