import json

import requests

import functions

group_ids = ["15458819"]
page_groups = []

for group_id in group_ids:
    success = functions.get_pages(group_id)
    # If downloading the pages led to an error
    if not success[1]:
        # The function returns all the pages it downloaded before it stopped running, so we save those
        page_groups.append(success[0])
        # Check if the function downloaded any pages before returning
        # The -1 is for getting the last group downloaded
        if 0 < len(page_groups[-1]):
            # if it did, get the last pages cursor and use that as an argument, to start again where it ended
            cursor_left_off_on = page_groups[-1][-1]["nextPageCursor"]
            if cursor_left_off_on:
                # Wait for the rate limit to end (Should be 45~ seconds)
                functions.wait_ratelimit()
                success = functions.get_pages(group_id, cursor=cursor_left_off_on)
        else:
            # If it didn't download any pages, restart without adding a cursor argument
            functions.wait_ratelimit()
            success = functions.get_pages(group_id)
    else:
        # If it finished without any issue, add it to the pages list
        page_groups.append(success[0])

for group in page_groups:
    for page in group:
        for asset in page["data"]:
            resp = requests.get("https://api.roblox.com/Marketplace/ProductInfo?assetId=" + str(asset["id"]))
            text = resp.text
            data = json.loads(text)
            print(data)