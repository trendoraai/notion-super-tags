from notion_client.errors import APIResponseError
from collections import namedtuple
from pprint import pprint
import logging

from tagz.utils import extract_name, wrapper_for_page_name
from tagz.exceptions import SubpageNotEmpty

logger = logging.getLogger(__name__)


class Database:
    _shared_state = {}

    def __init__(self, notion, database_id):
        self.__dict__ = self._shared_state
        if not self._shared_state:
            self.notion = notion
            self.database_id = database_id
            self.database = self.get_database()
            self.database_properties = self.database["properties"]
            self.ensure_integrity_of_database()

    def ensure_integrity_of_database(self):
        # Ensure the database has the required columns
        if not self.check_column_names():
            raise ValueError("Database doesn't have the required columns.")
        # Ensure there is no page without a title
        self.delete_pages_without_name()
        # Ensure there is no duplicate page with the same title
        self.merge_pages_with_same_name()

    def get_database(self):
        try:
            database = self.notion.databases.retrieve(database_id=self.database_id)
            return database
        except APIResponseError:
            message = (
                f"Invalid database ID: {self.database_id}. Please provide a valid UUID."
            )
            logger.error(message)
            raise SystemExit(message)

    def check_column_names(self):
        expected_columns = ["title", "Tags", "Created time", "Last edited time", "ID"]
        column_names = list(self.database_properties.keys())
        missing_columns = [col for col in expected_columns if col not in column_names]
        if missing_columns:
            message = (
                f"Column names: {', '.join(missing_columns)} not found in the database."
            )
            logger.error(message)
            return False
        return True

    def create_page(self, title, _children=None):
        # Ensure we don't create a duplicate page
        existing_page = self.get_page(title)
        if existing_page is not None:
            return existing_page

        new_page = self.notion.pages.create(
            parent={"database_id": self.database_id},
            properties=wrapper_for_page_name(title),
        )
        return new_page

    def get_page(self, title):
        # Query the database for the page with the given title
        results = self.notion.databases.query(
            database_id=self.database_id,
            filter={"or": [{"property": "title", "title": {"equals": title}}]},
        )

        # Iterate over the results and return the id of the page that matches the given title
        for page in results["results"]:
            if _get_page_title(page) == title:
                return page
        return None

    def delete_page(self, page_id):
        try:
            page = self.notion.pages.retrieve(page_id=page_id)
            if not page["archived"]:
                archived_page = self.notion.pages.update(page_id=page_id, archived=True)
                return archived_page
            else:
                return page
        except APIResponseError:
            logger.error(f"Page with ID: {page_id} does not exist.")
            return None

    def delete_pages_without_name(self):
        pages = self.notion.databases.query(database_id=self.database_id)["results"]

        # Iterate over all pages
        for page in pages:
            try:
                # Try to get the page title
                _ = _get_page_title(page)
            except IndexError:
                # If the page doesn't have a title, delete it
                self.delete_page(page["id"])

    def merge_pages_with_same_name(self):
        duplicate_pages = self._find_duplicate_pages()

        if duplicate_pages == {}:
            logger.info("No duplicate pages found.")
            return None

        self._merge_and_delete(duplicate_pages)

    def _find_duplicate_pages(self):
        pages = self.notion.databases.query(database_id=self.database_id)["results"]
        pages_dict = {}

        for page in pages:
            page_name = _get_page_title(page)
            row_id = str(page["properties"]["ID"]["unique_id"]["number"])
            page_tuple = namedtuple("Page", ["id", "row_id"])(page["id"], row_id)

            pages_dict.setdefault(page_name, []).append(page_tuple)
            pages_dict[page_name].sort(key=lambda x: x.row_id)

        return {k: v for k, v in pages_dict.items() if len(v) > 1}

    def _merge_and_delete(self, duplicate_pages):
        """
        This method merges pages with same names and delete the duplicate pages. It keeps the first page and merges content of rest of the pages into the first page.
        """
        # Merge the pages with the same title
        for page_name, page_tuples in duplicate_pages.items():
            self._log_page_info(page_name, page_tuples)
            target_page_id = page_tuples[0].id
            for page_tuple in page_tuples[1:]:
                self._move_blocks_and_delete_page(target_page_id, page_tuple)

    def _log_page_info(self, page_name, page_tuples):
        logger.info(
            f"Page title: {page_name}, Additional pages with same "
            f"title: {len(page_tuples) - 1}"
        )

    def _move_blocks_and_delete_page(self, target_page_id, page_tuple):
        logger.info(
            f"Moving blocks from page: {page_tuple.id} " f"to page: {target_page_id} "
        )
        blocks = self.notion.blocks.children.list(page_tuple.id)
        self._move_blocks_to_page(blocks, target_page_id)
        self.delete_page(page_tuple.id)

    def _move_blocks_to_page(self, blocks, target_page_id):
        for block in blocks["results"]:
            block["parent"] = {"page_id": target_page_id, "type": "page_id"}
            self.notion.blocks.children.append(
                block_id=target_page_id,
                children=[block],
            )

    def move_subpage_to_database(self, page_id):
        """
        A subpage is a page that is created somewhere within the page. Generally
        subpage is accompanied with text. The block type is generally paragraph
        containing normal text and subpage.

        These abandoned subpages are outside of the tags database. We want to
        move these subpages to the tags database such that there's a single
        source of truth.
        """
        blocks = self.notion.blocks.children.list(page_id)
        subpage = self.notion.pages.retrieve(page_id=page_id)
        title = extract_name(subpage)

        if blocks["results"]:
            raise SubpageNotEmpty(
                f"Subpage {title} contains blocks. Please remove the blocks and try again."
            )

        new_page = self.create_page(title)
        return new_page


def delete_block(notion, block_id):
    archived_block = notion.blocks.update(block_id=block_id, archived=True)
    return archived_block


def _get_page_title(page):
    return page["properties"]["title"]["title"][0]["plain_text"]
