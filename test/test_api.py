from pw import api
from pw.encrypt import encrypt, decrypt

from . import AccountFactory, BaseTestCase


class SingleAccountApiTests(BaseTestCase):
    def setUp(self):
        super(SingleAccountApiTests, self).setUp()
        self.acc = AccountFactory()

    def query(self):
        return self.session.query(AccountFactory.FACTORY_FOR)

    def test_create_account(self):
        self.data = dict(
            account="account",
            password="password",
            description="description",
        )
        acc = api.create_account(**self.data)
        self.assertIsNotNone(acc)
        acc = self.query().filter_by(id=acc.id).first()
        self.assertEqual(acc.raw_account, self.data["account"])
        self.assertEqual(acc.raw_password, self.data["password"])
        self.assertEqual(acc.description, self.data["description"])

    def test_change_password(self):
        new_password = "new password"
        acc = api.change_password(self.acc.raw_account, self.acc.raw_password, new_password)
        self.assertEqual(acc.raw_password, new_password)

        acc = api.change_password(self.acc.id, self.acc.raw_password, new_password)
        self.assertEqual(acc.raw_password, new_password)

        acc = api.change_password(self.acc.raw_account, "invalid password", new_password)
        self.assertIsNone(acc)

        acc = api.change_password("invalid account", self.acc.raw_password, new_password)
        self.assertIsNone(acc)

        invalid_id = -1
        acc = api.change_password(invalid_id, self.acc.raw_password, new_password)
        self.assertIsNone(acc)
