from src.tagz.database import create_page_in_database, delete_page

# TODO: Write a function to test if we've the permission to read the page
# even when outside of the database.


def assert_permission_to_create_and_delete_page(notion, page_id, database_id):
    """
    This function checks if the user has permission to create and delete
    pages in the database.

    User might NOT have the permission or the database might be locked or the database_id was invalid.

    For now, even if the database or page is locked, still we're able to create and delete pages within the database.

    TODO: Check if the page has similar behavior as the database when locked.
    """
    page_properties = {
        "Name": {"title": [{"text": {"content": "Temp Page to Test Permissions 4"}}]},
    }
    try:
        page = create_page_in_database(notion, database_id, page_properties)
        page_id = page["object"] == "page" and page["id"]

        archived_page = delete_page(notion, page_id)
        archived_page_id = archived_page["object"] == "page" and archived_page["id"]
        return archived_page_id == page_id
    except Exception as e:
        print("Exception: ", e)
        return False
