import unittest

import factory
from factory.alchemy import SQLAlchemyModelFactory

from pw import model
from pw.model import Account, session
from pw.encrypt import encrypt, decrypt


class AccountFactory(SQLAlchemyModelFactory):
    FACTORY_FOR = Account
    FACTORY_SESSION = session

    id = factory.Sequence(lambda n: n)
    description = "THIS IS A DESCRIPTION"

    @factory.lazy_attribute
    def raw_account(self):
        return "account_{id}".format(id=self.id)

    @factory.lazy_attribute
    def raw_password(self):
        return "password_{id}".format(id=self.id)


class ModelAccountTest(unittest.TestCase):
    def setUp(self):
        self.acc = AccountFactory()

    def test_account_factory(self):
        """check AccountFactory instance has valid account"""
        account = encrypt(self.acc.raw_account)
        self.assertEqual(self.acc.account, account)

        account = encrypt("account_{id}".format(id=self.acc.id))
        self.assertEqual(self.acc.account, account)

        # so far, becaouse the same algorithm for password is used
        # don't repeat to check password

    def test_change_master_key(self):
        # first backup data
        account = self.acc.account
        password = self.acc.password
        acc = self.acc.change_master_key("a new master key")

        # encrypted strings have changed
        self.assertNotEqual(account, self.acc.account)
        self.assertNotEqual(password, acc.password)

        # decrypted strings are still same
        self.assertEqual(acc, self.acc)
        self.assertEqual(acc.raw_account, self.acc.raw_account)
        self.assertEqual(acc.raw_password, self.acc.raw_password)


class ModelAccountManagerTest(unittest.TestCase):
    def setUp(self):
        self.query = Account.query
        self.acc = AccountFactory()
        session.add(self.acc)
        session.commit()
        self.not_duplicated_id = self.acc.id + 1
        self.not_duplicated_account = "NOT DUPLICATED ACCOUNT!"

    ### __getattribute__
    def test__getattribute__(self):
        import sqlalchemy as sql
        self.assertIsInstance(self.query, model.AccountManager)
        self.assertIs(self.query.exists.im_self, model.AccountManager)
        self.assertIs(self.query.create.im_self, model.AccountManager)
        self.assertIs(self.query.all.im_class, sql.orm.query.Query)
        with self.assertRaises(AttributeError):
            self.assertIsNone(self.query.foobaa)

    ### get_by_id_or_account
    def test_get_by_id_or_account(self):
        acc = self.query.get_by_id_or_account(self.acc.id)
        self.assertEqual(acc.id, self.acc.id)

    def test_get_by_id_or_account__with_account(self):
        acc = self.query.get_by_id_or_account(self.acc.raw_account)
        self.assertEqual(acc.id, self.acc.id)

    def test_get_by_id_or_account__return_none(self):
        acc = self.query.get_by_id_or_account(self.not_duplicated_id)
        self.assertIsNone(acc)

    ### exists
    def test_exists(self):
        self.assertTrue(self.query.exists(id=self.acc.id))
        self.assertTrue(self.query.exists(raw_account=self.acc.raw_account))

        # no entities
        self.assertFalse(self.query.exists(id=self.not_duplicated_id))
        self.assertFalse(self.query.exists(raw_account=self.not_duplicated_account))

    ### create
    def test_create(self):
        account = "account"
        password = "password"
        description = "description"
        acc = self.query.create(account, password, description)
        self.assertEqual(acc.raw_account, account)
        self.assertEqual(acc.raw_password, password)
        self.assertEqual(acc.description, description)

    def test_create__duplication_error(self):
        with self.assertRaises(ValueError):
            self.query.create(self.acc.raw_account, "password")

if __name__ == '__main__':
    unittest.main()
