from dotenv import load_dotenv
from collections import OrderedDict
from pprint import pprint
from notion_client import Client
import os

from tagz.extract import extract_text, extract_mention_href_text


def main():
    # Load the environment variables
    load_dotenv()

    # Initialize Notion client with your integration token
    notion = Client(auth=os.getenv("NOTION_TOKEN"))

    # Replace this with the ID of the page you want to retrieve
    page_id = os.getenv("PAGE_ID_FOR_MENTIONS")

    # Retrieve the page
    page = notion.pages.retrieve(page_id=page_id)

    # Print the page title
    pprint(page)
    title = page["properties"]["Name"]["title"][0]["plain_text"]
    print(title)

    # Retrieve the blocks of the page
    blocks = notion.blocks.children.list(page_id)

    # Print each block
    to_print = []
    for block in blocks["results"]:
        pprint(block)
        text = extract_text(block)
        extracted_mention = extract_mention_href_text(block)
        to_print.append({block["type"]: extracted_mention})
    pprint(to_print)
    # import json
    # with open('tests/tests_data/api_response_for_blocks_with_mentions.json', 'w') as f:
    #     json.dump(to_print, f)


if __name__ == "__main__":
    main()
