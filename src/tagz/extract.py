def extract_text(block):
    block_type = block["type"]
    if block_type in [
        "paragraph",
        "heading_1",
        "heading_2",
        "heading_3",
        "bulleted_list_item",
        "numbered_list_item",
        "to_do",
        "toggle",
    ]:
        rich_text = block[block_type]["rich_text"]
        if rich_text:
            return rich_text[0]["plain_text"]
    return None


def extract_mention_href_text(block):
    block_type = block["type"]
    if block_type in [
        "paragraph",
        "heading_1",
        "heading_2",
        "heading_3",
        "bulleted_list_item",
        "numbered_list_item",
        "to_do",
        "toggle",
    ]:
        rich_text = block[block_type].get("rich_text", [])
        extracted_data = []
        for text in rich_text:
            if text["type"] == "mention":
                mention = text.get("mention", None)
                href = text.get("href", None)
                plain_text = text.get("plain_text", None)
                extracted_data.append(
                    {"mention": mention, "href": href, "plain_text": plain_text}
                )
        return extracted_data if extracted_data else None
    return None
