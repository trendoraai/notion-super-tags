def extract_name(page):
    if page["parent"]["type"] in ["database_id", "block_id", "page_id"]:
        return page["properties"]["title"]["title"][0]["text"]["content"]
    raise Exception("Unknown parent type")


def wrapper_for_page_name(title):
    return {
        "title": {"title": [{"text": {"content": title}}]},
    }
