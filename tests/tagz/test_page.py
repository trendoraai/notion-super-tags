from src.tagz.page import write_content_to_page
from src.tagz.database import get_page_with_name, delete_block
import pytest


def test_write_content_to_page(notion, database_id):
    """
    This test ensures the functionality of writing content to a page.
    """
    # We only want to write content within the TAGS database
    predefined_page_name = "_development"
    page = get_page_with_name(notion, database_id, predefined_page_name)

    if page is None:
        raise FileNotFoundError(
            f"The page with the name {predefined_page_name} was not found in database: {database_id}."
        )

    page_id = page["id"]

    # Call the function with test inputs
    content = "This is test content"
    updated_page = write_content_to_page(notion, page_id, content)

    # Assert that the updated page has the expected content
    assert (
        updated_page["results"][0]["paragraph"]["rich_text"][0]["text"]["content"]
        == content
    )

    # Clean up
    delete_block(notion, updated_page["results"][0]["id"])
