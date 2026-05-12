import factory
from factory import Faker

from app.common.security import generate_salt, hash_password
from app.domains.identity.model import User
from app.domains.items.model import Item


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = Faker("email")
    hashed_password = factory.LazyAttribute(
        lambda _: hash_password("Password123", generate_salt()),
    )
    password_salt = factory.LazyAttribute(lambda _: generate_salt())
    is_active = True
    is_superuser = False


class ItemFactory(factory.Factory):
    class Meta:
        model = Item

    title = Faker("sentence", nb_words=3)
    description = Faker("text", max_nb_chars=200)
    is_public = False
