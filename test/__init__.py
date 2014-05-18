import factory
from factory.alchemy import SQLAlchemyModelFactory

from pw.model import Account, session


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
