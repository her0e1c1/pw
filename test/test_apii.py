import unittest

from pw import api
from pw.encrypt import encrypt, decrypt

from . import AccountFactory, BaseTestCase


class ApiTests(BaseTestCase):
    def setUp(self):
        super(ApiTests, self).setUp()
        self.Account = AccountFactory.FACTORY_FOR
        self.data = dict(
            account="account",
            password="password",
            description="description",
        )

    def query(self):
        return self.session.query(self.Account)

    def test_create_account(self):
        acc = api.create_account(**self.data)
        self.assertIsNotNone(acc)
        acc = self.query().filter_by(id=acc.id).first()
        self.assertEqual(acc.raw_account, self.data["account"])

if __name__ == '__main__':
    unittest.main()
