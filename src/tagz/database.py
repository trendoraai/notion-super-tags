from notion_client.errors import APIResponseError


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
        print(f"Invalid database ID: {database_id}. Please provide a valid UUID.")
        raise SystemExit


def create_page_in_database(notion, database_id, page_properties):
    new_page = notion.pages.create(
        parent={"database_id": database_id}, properties=page_properties
    )
    return new_page


def delete_page(notion, page_id):
    archived_page = notion.pages.update(page_id=page_id, archived=True)
    return archived_page


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
