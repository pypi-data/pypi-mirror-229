import asyncio
import pytest
from django.contrib.auth.models import User

username = "test_admin"
password = "test_admin"
email = "test_email@localhost"


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    This fixture enables database access for all tests.
    """
    pass


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        User.objects.create(username=username, password=password, email=email)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def user():
    return User.objects.get(username=username)


@pytest.fixture
async def auser():
    return await User.objects.aget(username=username)


def test_djasa_settings():
    from djasa.conf.settings import DjasaSettings

    settings = DjasaSettings()
    settings.validate()
