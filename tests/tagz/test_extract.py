from collections import OrderedDict
import json
import pytest
import os
from src.tagz.extract import extract_text, extract_mention_href_text


def test_extract_text():
    block = {
        "type": "paragraph",
        "paragraph": {"rich_text": [{"plain_text": "Hello, world!"}]},
    }
    result = extract_text(block)
    assert result == "Hello, world!"


def test_api_response_for_text_from_different_block_types(
    notion, page_id_to_test_basic_text
):
    """
    This test checks if the API or API response from Notion has changed
    for the the simple text. I've already locked the page_id (within
    Notion) so that the content of the page_id should never change.

    If the API or API response changes in the future, we'll know because
    this test will fail.
    """
    blocks = notion.blocks.children.list(page_id_to_test_basic_text)

    result = []
    for block in blocks["results"]:
        text = extract_text(block)
        result.append([block["type"], text])

    assert result == [
        ["paragraph", "Hello World from Notion"],
        ["paragraph", None],
        ["heading_1", "Hello Heading 1"],
        ["heading_1", None],
        ["heading_2", "Hello Heading 2"],
        ["heading_3", "Hello Heading 3"],
        ["bulleted_list_item", "Hello bullet list"],
        ["bulleted_list_item", None],
        ["numbered_list_item", "Hello numbered list"],
        ["numbered_list_item", None],
        ["to_do", "Hello To-Do"],
        ["to_do", None],
        ["toggle", "Hello Toggle"],
        ["toggle", None],
        ["paragraph", None],
    ]


def test_api_response_for_blocks_with_mentions(notion, page_id_to_test_mentions):
    """
    This checks if the API or API response for mentions within Notion
    has changed.
    """
    blocks = notion.blocks.children.list(page_id_to_test_mentions)

    result = []
    for block in blocks["results"]:
        text = extract_mention_href_text(block)
        result.append({block["type"]: text})

    with open("tests/tests_data/api_response_for_blocks_with_mentions.json", "r") as f:
        truth = json.load(f)

    assert result == truth
