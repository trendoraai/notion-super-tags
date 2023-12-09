from dotenv import load_dotenv
from collections import OrderedDict
from pprint import pprint
from notion_client import Client
import logging
import os

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


def main():
    # Load the environment variables
    load_dotenv()

    # Initialize Notion client with your integration token
    notion = Client(auth=os.getenv("NOTION_TOKEN"))
    database_id = os.getenv("SUPERTAGS_DATABASE_ID")
    root_page_id = os.getenv("ROOT_PAGE_ID")
    subpage_id = os.getenv("SUBPAGE_WITHIN_BLOCK_ID")
    regular_page_id = os.getenv("REGULAR_PAGE_WITHIN_PAGE_ID")
    block_id_with_supertags = os.getenv("BLOCK_ID_WITH_SUPERTAGS")

    supertags_database = Database(notion, database_id)

    # TODO: What happens if we want to append at the first first position?
    previous_block_id = None
    for block_data in notion.blocks.children.list(block_id=root_page_id)["results"]:
        block = Block(
            notion,
            block_data["id"],
            supertags_database,
            block_data,
            above_block_id=previous_block_id,
        )
        previous_block_id = block_data["id"]
        updated_data = block.create_original_synced_block()
        appended_children = block.append_children_to_original_block(updated_data["id"])
        pprint(appended_children)
        supertags = block.extract_supertags()
        for supertag in supertags:
            supertag_id = extract_id(supertag)
            supertag_homepage = Homepage(notion, supertag_id, database_id)
            duplicated_block = supertag_homepage.append_synced_block(
                extract_id(updated_data)
            )
        input("Press Enter to continue...")


if __name__ == "__main__":
    main()
