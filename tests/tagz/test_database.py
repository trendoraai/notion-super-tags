import pytest
from pprint import pprint
from src.tagz.database import create_page_in_database, delete_page, get_page_with_name


def test_page_creation_and_deletion_in_a_database(notion, database_id):
    """
    This test ensures the end-to-end functionality of creating and deleting
    a page within a database.
    """
    page_properties = {
        "Name": {"title": [{"text": {"content": "Temp Page to Test Permissions 4"}}]},
    }
    to_create_page = create_page_in_database(notion, database_id, page_properties)
    page_id = to_create_page["object"] == "page" and to_create_page["id"]

    created_page = notion.pages.retrieve(page_id=page_id)
    created_page_id = created_page["object"] == "page" and created_page["id"]

    assert created_page_id == page_id

    archived_page = delete_page(notion, page_id)
    archived_page_id = archived_page["object"] == "page" and archived_page["id"]

    archived_page_to_check = notion.pages.retrieve(page_id=page_id)
    assert (
        archived_page_to_check["id"] == page_id
        and archived_page_to_check["archived"] == True
    )


def test_get_page_with_name(notion, database_id):
    # This page is already created in the TAGS database
    predefined_page_name = "_development"
    page = get_page_with_name(notion, database_id, predefined_page_name)
    assert page is not None
