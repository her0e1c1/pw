from mock import patch

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

    def test_delete_by_id__no_id(self):
        acc = api.delete_by_id(self.acc.id + 1)
        self.assertIsNone(acc)

    def test_delete_by_id__say_yes(self):
        with patch("pw.api.ask_yes_or_no") as m:
            m.return_value = True
            acc = api.delete_by_id(self.acc.id)
        count = self.query().filter_by(id=acc.id).count()
        self.assertEqual(len(self.query().all()), count)

    def test_delete_by_id__say_no(self):
        with patch("pw.api.ask_yes_or_no") as m:
            m.return_value = False
            acc = api.delete_by_id(self.acc.id)
        self.assertIsNone(acc)
        self.assertEqual(len(self.query().all()), 1)


class MultiAccountsApiTests(BaseTestCase):
    def setUp(self):
        super(MultiAccountsApiTests, self).setUp()
        self.account_list = [AccountFactory() for _ in range(10)]

    def query(self):
        return self.session.query(AccountFactory.FACTORY_FOR)

    def test_delete_all_accounts__say_yes(self):
        with patch("pw.api.ask_yes_or_no") as m:
            m.return_value = True
            api.delete_all_accounts()
        count = len(self.query().all())
        self.assertEqual(count, 0)

    def test_delete_all_accounts__say_no(self):
        with patch("pw.api.ask_yes_or_no") as m:
            m.return_value = False
            rv = api.delete_all_accounts()
        self.assertIsNone(rv)
        count = len([self.query().filter_by(id=acc.id) for acc in self.account_list])
        self.assertEqual(len(self.account_list), count)
