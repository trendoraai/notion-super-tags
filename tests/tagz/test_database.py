import pytest
from pprint import pprint

# from src.tagz.page import write_content_to_page, get_paragraph_block_content
from src.tagz.database import Database


def test_page_creation_and_deletion(notion, database):
    """
    This test ensures the end-to-end functionality of creating and deleting
    a page within a database.
    """
    name = "Temp page to test page creation and deletion"
    page = database.create_page(name)
    page_id = page["object"] == "page" and page["id"]

    created_page = notion.pages.retrieve(page_id=page_id)
    created_page_id = created_page["object"] == "page" and created_page["id"]

    assert created_page_id == page_id

    created_page_name = created_page["properties"]["Name"]["title"][0]["text"][
        "content"
    ]
    assert name == created_page_name

    _ = database.delete_page(page_id)
    archived_page_to_check = notion.pages.retrieve(page_id=page_id)
    assert (
        archived_page_to_check["id"] == page_id
        and archived_page_to_check["archived"] == True
    )


# def test_get_page_with_name(notion, database_id):
#     # This page is already created in the TAGS database
#     predefined_page_name = "_development"
#     page = get_page_with_name(notion, database_id, predefined_page_name)
#     assert page is not None


# @pytest.fixture
# def setup_pages(notion, database_id):
#     # Create three pages with the same name and different content
#     page_name = "This is a page which will have duplicates"
#     page_properties = {
#         "Name": {"title": [{"text": {"content": page_name}}]},
#     }
#     first_page = create_page_in_database(notion, database_id, page_properties)
#     first_page_id = first_page["object"] == "page" and first_page["id"]
#     first_page_content = "This is the content of the first page."
#     _ = write_content_to_page(notion, first_page_id, get_paragraph_block_content(first_page_content))

#     second_page = create_page_in_database(notion, database_id, page_properties)
#     second_page_id = second_page["object"] == "page" and second_page["id"]
#     second_page_content = "This is the content of the second page."
#     _ = write_content_to_page(notion, second_page_id, get_paragraph_block_content(second_page_content))

#     third_page = create_page_in_database(notion, database_id, page_properties)
#     third_page_id = third_page["object"] == "page" and third_page["id"]
#     third_page_content = "This is the content of the third page."
#     _ = write_content_to_page(notion, third_page_id, get_paragraph_block_content(third_page_content))

#     yield first_page_id, first_page_content, second_page_content, third_page_content

#     # Teardown: Delete the pages after test
#     delete_page(notion, first_page_id)
#     delete_page(notion, second_page_id)
#     delete_page(notion, third_page_id)


# def test_merge_pages_with_same_name(notion, database_id, setup_pages):
#     (
#         first_page_id,
#         first_page_content,
#         second_page_content,
#         third_page_content,
#     ) = setup_pages
#     """
#     This test ensures the functionality of merging pages with the same name.
#     """
#     # Merge the pages with the same name
#     merge_pages_with_same_name(notion, database_id)

#     # Check the content blocks of the first page
#     first_page_content_blocks = notion.blocks.children.list(first_page_id)

#     # Check if the first page has the content of the first, second and
#     # third page
#     assert (
#         first_page_content_blocks["results"][0]["paragraph"]["rich_text"][0]["text"][
#             "content"
#         ]
#         == first_page_content
#     )

#     assert (
#         first_page_content_blocks["results"][1]["paragraph"]["rich_text"][0]["text"][
#             "content"
#         ]
#         == second_page_content
#     )

#     assert (
#         first_page_content_blocks["results"][2]["paragraph"]["rich_text"][0]["text"][
#             "content"
#         ]
#         == third_page_content
#     )


# """TODO: In the codebase, we'll always use subpage and not sub-page or sub_page"""
# # TODO: Follow a convention such that database_id is before page_id.


# @pytest.fixture
# def delete_the_newly_moved_subpage(notion, subpage_id, database_id, request):
#     # Setup: Nothing to do before the test

#     yield

#     # Teardown: Code to run after the test
#     # Retrieve the new_subpage from the request.node
#     new_subpage = request.node.new_subpage
#     # Assuming you have a function to move the subpage back to its original database
#     delete_page(notion, new_subpage["id"])


# def test_move_subpage_to_tags_database(
#     notion, database_id, subpage_id, delete_the_newly_moved_subpage, request
# ):
#     """
#     This test checks if the sub-page is moved correctly to the tags database.
#     """
#     original_subpage = notion.pages.retrieve(page_id=subpage_id)
#     new_subpage = move_subpage_to_tags_database(notion, database_id, subpage_id)
#     # Store the new_subpage in the request.node so it can be accessed in the fixture
#     request.node.new_subpage = new_subpage
#     assert new_subpage["parent"]["database_id"].replace("-", "") == database_id.replace(
#         "-", ""
#     )
#     assert (
#         new_subpage["properties"]["Name"]["title"][0]["text"]["content"]
#         == original_subpage["properties"]["title"]["title"][0]["text"]["content"]
#     )
