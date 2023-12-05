from dotenv import load_dotenv
from collections import OrderedDict
from pprint import pprint
from notion_client import Client
import os

from tagz.extract import extract_text, extract_mention_href_text
from tagz.database import (
    get_column_names,
    assert_column_names,
    create_page_in_database,
    delete_page,
    get_page_with_name,
)
from tagz.page import write_content_to_page
from tagz.permissions import assert_permission_to_create_and_delete_page


def main():
    # Load the environment variables
    load_dotenv()

    # Initialize Notion client with your integration token
    notion = Client(auth=os.getenv("NOTION_TOKEN"))

    # Replace this with the ID of the page you want to retrieve
    page_id = os.getenv("PAGE_ID_FOR_MENTIONS")

    # Retrieve the page properties
    page = notion.pages.retrieve(page_id=page_id)

    # Print the page title
    pprint(page)
    title = page["properties"]["Name"]["title"][0]["plain_text"]
    print(title)

    # Retrieve the blocks of the page
    blocks = notion.blocks.children.list(page_id)

    # # Print each block
    # to_print = []
    # for block in blocks["results"]:
    #     pprint(block)
    #     text = extract_text(block)
    #     extracted_mention = extract_mention_href_text(block)
    #     to_print.append({block["type"]: extracted_mention})
    # pprint(to_print)
    # # import json
    # # with open('tests/tests_data/api_response_for_blocks_with_mentions.json', 'w') as f:
    # #     json.dump(to_print, f)

    # High-level API
    # Extract all blocks on the page
    # Keep only the blocks that have tags (mentions)
    # Extract the tags from the blocks
    # Extract the tag page for each block
    # Append the block to the tag page

    database_id = os.getenv("TAGS_DATABASE_ID")
    column_names = get_column_names(notion, database_id)
    print(
        assert_column_names(
            notion, database_id, ["Name", "Tags", "Created time", "Last edited time"]
        )
    )
    print(column_names)

    print(assert_permission_to_create_and_delete_page(notion, page_id, database_id))

    name = "_development"

    tag_page = get_page_with_name(notion, database_id, name)

    print(tag_page)

    if tag_page is None:
        tag_page = create_page_in_database(
            notion,
            database_id,
            {
                "Name": {"title": [{"text": {"content": name}}]},
            },
        )

    page_id = tag_page["object"] == "page" and tag_page["id"]
    content = "This is some new ass content."
    updated_page = write_content_to_page(notion, page_id, content)
    print(updated_page)


if __name__ == "__main__":
    main()
