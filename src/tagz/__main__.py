from dotenv import load_dotenv
from collections import OrderedDict
from notion_client import Client
import logging
import os
import click
import time

from tagz.extract import extract_text, extract_mention_href_text
from tagz.database import Database
from tagz.block import Block, extract_id
from tagz.page import Homepage

logging.basicConfig(
    filename="app.log",
    filemode="w",
    format="%(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--root_page_id", default=None, help="Root page ID")
def main(root_page_id=None):
    # Load the environment variables
    load_dotenv()

    # Initialize Notion client with your integration token
    notion = Client(auth=os.getenv("SECONDARY_NOTION_TOKEN"))
    database_id = os.getenv("TAGS_DATABASE_ID")
    # If root_page_id is not passed as an argument, get it from environment variables
    if not root_page_id:
        root_page_id = os.getenv("ROOT_PAGE_ID")

    supertags_database = Database(notion, database_id)

    # TODO: What happens if we want to append at the first first position?
    previous_block_id = None
    for block_data in notion.blocks.children.list(block_id=root_page_id)["results"]:
        start_time = time.time()  # Start timing
        block = Block(
            notion,
            block_data["id"],
            supertags_database,
            block_data,
            above_block_id=previous_block_id,
        )
        # Cannot move this line. We need the previous_block_id.
        previous_block_id = block_data["id"]
        if not block.supertags:
            end_time = time.time()  # End timing
            print(f"Time taken for block {block_data['id']}: {end_time - start_time} seconds")
            continue
        synced_wrapper = block.create_original_synced_block()

        # previous_block_id should be updated because we have created a new block and we're doing to delete the old block.
        previous_block_id = synced_wrapper["id"]
        block.append_children_to_original_block(synced_wrapper["id"])

        for supertag in block.supertags:
            supertag_id = extract_id(supertag)
            supertag_homepage = Homepage(notion, supertag_id, database_id)
            _ = supertag_homepage.append_synced_block(
                synced_wrapper["id"]
            )
        block.delete_block_from_notion()

        end_time = time.time()  # End timing
        print(f"Time taken for block {block_data['id']}: {end_time - start_time} seconds")


if __name__ == "__main__":
    main()
