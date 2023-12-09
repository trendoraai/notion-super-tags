# Step 1: Ensure supertags exist in the database.
# Step 2: Ensure supertags are unique.
from typing import Any, Dict, List
from tagz.page import Homepage
from pprint import pprint


class Block:
    def __init__(
        self, notion, block_id, database, block_data=None, above_block_id=None
    ) -> None:
        self.notion = notion
        self.block_id = block_id
        self.supertags_database = database
        self.supertags_database_id = database.database_id
        self.data = block_data or self.get_block_data()
        # The block that is above the current block. We need this
        # to remember the order of the blocks.
        self.above_block_id = above_block_id

        self.ensure_supertags_in_database()

    @property
    def supertags(self):
        return self.extract_supertags()

    @property
    def block_type(self):
        return self.data["type"]

    @property
    def parent_type(self):
        return self.data["parent"]["type"]

    @property
    def parent_id(self):
        return self.data["parent"][self.parent_type]

    @property
    def block_type(self):
        return self.data["type"]

    def ensure_supertags_in_database(self):
        for supertag in self.supertags:
            supertag_id = extract_id(supertag)
            if not self.is_supertag_in_database(supertag_id):
                print(f"Supertag {supertag['plain_text']} is not in database.")
                # move supertag to database
                new_page_id = self.supertags_database.move_subpage_to_database(
                    supertag_id
                )["id"]
                # change the supertag id in the block
                self.update_supertag(supertag_id, new_page_id)
                # self.notion.blocks.update(
                #     block_id=self.block_id,
                #     **{self.block_type: self.data[self.block_type]},
                # )

    def is_supertag_in_database(self, supertag_id):
        supertag_homepage = Homepage(
            self.notion, supertag_id, self.supertags_database_id
        )
        return supertag_homepage.is_in_database

    def update_supertag(self, old_page_id, new_page_id):
        original_rich_text = self.data[self.block_type]["rich_text"]
        for i, item in enumerate(original_rich_text):
            if (
                item["type"] == "mention"
                and item["mention"]["page"]["id"] == old_page_id
            ):
                updated_item = item.copy()
                updated_item["mention"]["page"]["id"] = new_page_id
                updated_item[
                    "href"
                ] = f"https://www.notion.so/{new_page_id.replace('-', '')}"
                original_rich_text[i] = updated_item
                break
        self.data[self.block_type]["rich_text"] = original_rich_text

    def get_block_data(self):
        return self.notion.blocks.retrieve(block_id=self.block_id)

    def is_supported_block_type(self):
        return self.block_type in [
            "paragraph",
            "heading_1",
            "heading_2",
            "heading_3",
            "bulleted_list_item",
            "numbered_list_item",
            "to_do",
            "toggle",
        ]

    def extract_supertags(self) -> List[Dict[str, Any]]:
        """
        This is what a single supertag looks like:
        {
            "annotations": {
            "bold": false,
            "code": false,
            "color": "default",
            "italic": false,
            "strikethrough": false,
            "underline": false
            },
            "href": "https://www.notion.so/<random-id>",
            "mention": {
            "page": {
                "id": "<random-id>"
            },
            "type": "page"
            },
            "plain_text": "_first",
            "type": "mention"
        }
        """
        if not self.is_supported_block_type():
            return []
        content = self.data[self.block_type]["rich_text"]
        supertags = [
            item
            for item in content
            if item["type"] == "mention" and item["plain_text"].startswith("_")
        ]
        return supertags
    
    
    def _extract_block_children(self):
        if self.data["has_children"]:
            return self.notion.blocks.children.list(block_id=self.block_id)["results"]
        return []
    

    def create_original_synced_block(self):
        if not len(self.supertags) > 0:
            return self.data
        content = {
            "type": "synced_block",
            "synced_block": {
                "synced_from": None,
                "children": [
                    {
                        "type": self.block_type,
                        self.block_type: self.data[self.block_type]
                    }
                ],
            },
        }
        # Notion API returns all the blocks that come the "after" block
        # (in this case, blocks that come after the above block)
        blocks_after_above_block = self.notion.blocks.children.append(
            block_id=self.parent_id, children=[content], after=self.above_block_id
        )
        original_synced_block = blocks_after_above_block["results"][0]
        assert original_synced_block["type"] == "synced_block"
        """ 
        {'archived': False,
            'created_by': {'id': '<random-id>', 'object': 'user'},
            'created_time': '2023-12-08T17:03:00.000Z',
            'has_children': True,
            'id': '<random-id>',
            'last_edited_by': {'id': '<random-id>',
                                'object': 'user'},
            'last_edited_time': '2023-12-08T17:03:00.000Z',
            'object': 'block',
            'parent': {'page_id': '<random-id>',
                        'type': 'page_id'},
            'synced_block': {'synced_from': None},
            'type': 'synced_block'
        }
        """
        return original_synced_block
    
    def append_children_to_original_block(self, original_synced_block_id):
        if self.data["has_children"] and self.supertags:
            parent_block_id = self.notion.blocks.children.list(block_id=original_synced_block_id)["results"][0]["id"]
            # children = self._extract_block_children()
            # pprint(children)
            # return self.notion.blocks.children.append(
                # block_id=parent_block_id, children=children)
            return self.deep_copy(self.block_id, parent_block_id)
        return None

    def deep_copy(self, copy_from_block_id, copy_to_block_id):
        # Retrieve the data from the source block
        source_block_data = self.notion.blocks.retrieve(block_id=copy_from_block_id)

        # Copy the data to the destination block
        self.notion.blocks.update(block_id=copy_to_block_id, **source_block_data)

        # Retrieve the children of the source block
        source_children = self.notion.blocks.children.list(block_id=copy_from_block_id)["results"]

        # For each child of the source block
        for source_child in source_children:
            # Create a new block in the destination block
            new_block = self.notion.blocks.children.append(block_id=copy_to_block_id, children=[{
                "type": source_child["type"],
                source_child["type"]: source_child[source_child["type"]]
            }])["results"][0]

            # Recursively copy the child block and its children
            self.deep_copy(source_child["id"], new_block["id"])


def extract_id(block):
    if block["type"] == "mention":
        return block["mention"]["page"]["id"]
    return block["id"]
