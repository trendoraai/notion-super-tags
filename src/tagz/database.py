from notion_client.errors import APIResponseError
from collections import namedtuple
from pprint import pprint
import logging

logger = logging.getLogger(__name__)


def assert_column_names(notion, database_id, expected_column_names):
    """
    This function checks if the expected_column_names are present in the
    database.

    If the expected_column_names are not present, then we cannot ensure
    the database properties.
    """
    column_names = get_column_names(notion, database_id)
    for column_name in expected_column_names:
        if column_name not in column_names:
            return False
    return True


def get_column_names(notion, database_id):
    database = get_database(notion, database_id)
    properties = database["properties"]
    column_names = [name for name in properties.keys()]
    return column_names


def get_database(notion, database_id):
    try:
        database = notion.databases.retrieve(database_id=database_id)
        return database
    except APIResponseError:
        logger.error(
            f"Invalid database ID: {database_id}. Please provide a valid UUID."
        )
        raise SystemExit


def create_page_in_database(notion, database_id, page_properties):
    new_page = notion.pages.create(
        parent={"database_id": database_id}, properties=page_properties
    )
    return new_page


def delete_page(notion, page_id):
    page = notion.pages.retrieve(page_id=page_id)
    if not page["archived"]:
        archived_page = notion.pages.update(page_id=page_id, archived=True)
        return archived_page
    else:
        return None


def delete_block(notion, block_id):
    archived_block = notion.blocks.update(block_id=block_id, archived=True)
    return archived_block


def get_page_with_name(notion, database_id, name):
    database = get_database(notion, database_id)

    # Query the database for the page with the given name
    results = notion.databases.query(
        database_id=database_id,
        filter={"or": [{"property": "Name", "title": {"equals": name}}]},
    )

    # Iterate over the results and return the id of the page that matches the given name
    for page in results["results"]:
        if page["properties"]["Name"]["title"][0]["plain_text"] == name:
            return page

    return None


def merge_pages_with_same_name(notion, database_id):
    """
    This function merges the pages with the same name in the tags database.

    This function is useful when we want to merge the pages with the same name
    in the database.
    """
    duplicate_pages = find_duplicate_pages(notion, database_id)

    if duplicate_pages == {}:
        logger.info("No duplicate pages found.")
        return None

    merge_and_delete_duplicate_pages(notion, duplicate_pages)


def merge_and_delete_duplicate_pages(notion, duplicate_pages):
    """
    This function merges the pages with the same name and delete the duplicate pages. It just keeps the first page and merges the rest of the pages into the first page.
    """
    # Merge the pages with the same name
    for page_name, page_tuples in duplicate_pages.items():
        logger.info(
            f"Page name: {page_name}, Additional pages with same "
            f"name: {len(page_tuples) - 1}"
        )
        # We want to merge all pages after the first page into
        # the first page.
        to_page = page_tuples[0].id
        for page_tuple in page_tuples[1:]:
            logger.info(
                f"Moving blocks from page: {page_tuple.id} "
                f"created on: {page_tuple.row_id} "
                f"to page: {to_page} "
                f"created time: {page_tuples[0].row_id}"
            )
            blocks = notion.blocks.children.list(page_tuple.id)

            # move these blocks to the first page
            for block in blocks["results"]:
                block["parent"] = {"page_id": to_page, "type": "page_id"}
                notion.blocks.children.append(
                    block_id=to_page,
                    children=[block],
                )

            # Delete the duplicate page
            delete_page(notion, page_tuple.id)


def delete_pages_without_name(notion, database_id):
    """
    This function deletes all the pages without a name in the database.

    Args:
        notion: The Notion client.
        database_id: The ID of the database.
    """
    # Get all the pages in the database
    pages = notion.databases.query(database_id=database_id)

    # Iterate over all pages
    for page in pages["results"]:
        try:
            # Try to get the page name
            page_name = page["properties"]["Name"]["title"][0]["plain_text"]
        except IndexError:
            # If the page doesn't have a name, delete it
            delete_page(notion, page["id"])


def find_duplicate_pages(notion, database_id):
    """
    This function finds all the pages with duplicate names in the database.

    Args:
        notion: The Notion client.
        database_id: The ID of the database.

    Returns:
        A dictionary with the page name as the key and a list of namedtuples
        (containing page id and row_id) as the value.
    """
    # TODO: Move out of this function: Delete any pages without a name
    delete_pages_without_name(notion, database_id)

    # Get all the pages in the database
    pages = notion.databases.query(database_id=database_id)

    # Create a dictionary with the page name as the key and the page id
    # and row_id as the value
    pages_dict = {}
    for page in pages["results"]:
        page_name = page["properties"]["Name"]["title"][0]["plain_text"]
        row_id = str(page["properties"]["ID"]["unique_id"]["number"])
        Page = namedtuple("Page", ["id", "row_id"])
        page_tuple = Page(page["id"], row_id)
        if page_name in pages_dict:
            pages_dict[page_name].append(page_tuple)

            # Ensure first page is the oldest page because we merge
            # rest of the pages into the first page.
            pages_dict[page_name] = sorted(
                pages_dict[page_name], key=lambda x: x.row_id
            )
        else:
            pages_dict[page_name] = [page_tuple]

    return {
        page_name: page_tuples
        for page_name, page_tuples in pages_dict.items()
        if len(page_tuples) > 1
    }


def move_subpage_to_tags_database(notion, database_id, page_id):
    """
    A sub-page is a page that is created somewhere within the page. Generally
    sub-page is accompanied with text. The block type is generally paragraph
    containing normal text and sub-page.

    These abandoned sub-pages are outside of the tags database. We want to
    move these sub-pages to the tags database such that there's a single
    source of truth.

    Ordering: first move subpage to SUPERTAGS database and then run the
    merge_pages_with_same_name function.
    """
    # Retrieve the sub-page
    sub_page = notion.pages.retrieve(page_id=page_id)

    # Create a new page in the tags database with the same properties as the sub-page
    # TODO: We just want to get the name from the sub-page. We don't want to get all the properties.
    # TODO: Check if the sub-page is NOT a page.
    # TODO: Check if the sub-page doesn't pre-exist in the tags database.
    # TODO: Check if the sub-page is NOT archived.
    # TODO: Check if the sub-page has a complete name and not just "_" or "".
    name = sub_page["properties"]["title"]["title"][0]["text"]["content"]
    new_page = create_page_in_database(
        notion,
        database_id,
        {
            "Name": {"title": [{"text": {"content": name}}]},
        },
    )

    # Move all blocks from the sub-page to the new page
    blocks = notion.blocks.children.list(page_id)
    for block in blocks["results"]:
        block["parent"] = {"page_id": new_page["id"], "type": "page_id"}
        notion.blocks.children.append(
            block_id=new_page["id"],
            children=[block],
        )

    return new_page
