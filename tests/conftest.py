from dotenv import load_dotenv
import sys
import os
import pytest
from notion_client import Client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


load_dotenv()


@pytest.fixture(scope="session")
def notion():
    return Client(auth=os.getenv("NOTION_TOKEN"))


@pytest.fixture(scope="session")
def page_id_to_test_basic_text():
    return os.getenv("PAGE_ID")


@pytest.fixture(scope="session")
def page_id_to_test_mentions():
    return os.getenv("PAGE_ID_FOR_MENTIONS")


@pytest.fixture(scope="session")
def database_id():
    return os.getenv("TAGS_DATABASE_ID")
