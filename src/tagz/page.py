import logging
from tagz.exceptions import SubpageNotEmpty

logger = logging.getLogger(__name__)


class Homepage:
    def __init__(self, notion, page_id, database_id):
        self.notion = notion
        self.page_id = page_id
        self.supertags_database_id = database_id
        self.page = self.get_page()

    @property
    def page_name(self):
        return self.page["properties"]["title"]["title"][0]["plain_text"]

    @property
    def parent_type(self):
        return self.page["parent"]["type"]

    @property
    def parent_id(self):
        return self.page["parent"][self.parent_type].replace("-", "")

    @property
    def is_in_database(self):
        return (
            self.parent_type == "database_id"
            and self.parent_id == self.supertags_database_id
        )

    @property
    def is_valid_supertag(self):
        return None  # This should be updated to reflect the actual condition

    def get_page(self):
        return self.notion.pages.retrieve(page_id=self.page_id)

    def append_synced_block(self, block_id):
        if not self.is_in_database:
            logger.info(
                f"Skipping the tag {self.page_name} because it's not in SUPERTAGS database."
            )
            return None
        content = {
            "type": "synced_block",
            "synced_block": {
                "synced_from": {"block_id": block_id},
            },
        }
        # duplicate_synced_block is a technical term from Notion API.
        # https://developers.notion.com/reference/block#synced-block
        duplicate_synced_block = self.notion.blocks.children.append(
            block_id=self.page_id, children=[content]
        )
        return duplicate_synced_block
