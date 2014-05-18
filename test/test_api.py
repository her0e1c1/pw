import unittest

from pw.model import AccountManager, autocommit
from pw.encrypt import encrypt, decrypt

from . import AccountFactory, BaseTestCase


Account = AccountFactory.FACTORY_FOR
session = AccountFactory.FACTORY_SESSION


class ModelAccountTests(BaseTestCase):

    def setUp(self):
        super(ModelAccountTests, self).setUp()
        self.acc = AccountFactory()

    def test_account_factory(self):
        """check AccountFactory instance has valid data"""
        # account
        account = encrypt(self.acc.raw_account)
        self.assertEqual(self.acc.account, account)

        account = encrypt("account_{id}".format(id=self.acc.id))
        self.assertEqual(self.acc.account, account)

        # password
        password = encrypt(self.acc.raw_password)
        self.assertEqual(self.acc.password, password)

        password = encrypt("password_{id}".format(id=self.acc.id))
        self.assertEqual(self.acc.password, password)

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


class ModelAccountManagerTests(BaseTestCase):
    def setUp(self):
        super(ModelAccountManagerTests, self).setUp()
        self.query = Account.query
        self.acc = AccountFactory()
        self.session.add(self.acc)
        self.session.commit()
        self.not_duplicated_id = self.acc.id + 1
        self.not_duplicated_account = "NOT DUPLICATED ACCOUNT!"

    ### __getattribute__
    def test__getattribute__(self):
        import sqlalchemy as sql
        self.assertIsInstance(self.query, AccountManager)
        self.assertIs(self.query.exists.im_self, AccountManager)
        self.assertIs(self.query.create.im_self, AccountManager)
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


class ModelAutocommitTests(BaseTestCase):
    def setUp(self):
        super(ModelAutocommitTests, self).setUp()
        self.query = Account.query
        self.account_list = []
        for _ in range(10):
            acc = AccountFactory()
            self.session.add(acc)
            self.account_list.append(acc)
        self.session.commit()
        self.count = self.current_count

    @property
    def current_count(self):
        return self.session.query(Account).count()

    def test_add(self):
        @autocommit()
        def f():
            return AccountFactory()
        f()
        self.assertEqual(self.count + 1, self.current_count)

    def test_add_multi(self):
        @autocommit()
        def f():
            for _ in range(size):
                yield AccountFactory()
        size = 5
        f()
        self.assertEqual(self.count + size, self.current_count)

    def test_delete(self):
        @autocommit(delete=True)
        def f():
            acc = self.account_list[0]
            return acc
        f()
        self.assertEqual(self.count - 1, self.current_count)

    def test_delete_multi(self):
        @autocommit(delete=True)
        def f():
            for acc in self.account_list:
                yield acc
        size = len(self.account_list)
        f()
        self.assertEqual(self.count - size, self.current_count)

if __name__ == '__main__':
    unittest.main()
