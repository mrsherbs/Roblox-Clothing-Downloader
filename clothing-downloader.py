import configparser
import time
import functions

config_file = "config.ini"
config = configparser.ConfigParser()
config.read(config_file)

# Downloader settings
save_directory = config.get("downloader", "save_directory")
group_ids = functions.convert_list(config.get("downloader", "group_ids").split(","), int)
exclude_offsale = functions.string_to_bool(config.get("downloader", "exclude_offsale"))
include_favorite_count = functions.string_to_bool(config.get("downloader", "include_favorites"))

page_groups = []
assets = []

# Download every page from these group IDs
# Each page contains a list of assets and info on them
for _, group_id in enumerate(group_ids):
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
                print("Retrying in 45 seconds...")
                time.sleep(45)
                success = functions.get_pages(group_id, cursor=cursor_left_off_on)
        else:
            # If it didn't download any pages, restart without adding a cursor argument
            print("Retrying in 45 seconds...")
            time.sleep(45)
            success = functions.get_pages(group_id)
    else:
        # If it finished without any issue, add it to the pages list
        page_groups.append(success[0])

# From every page, get every asset's info and add it to a list
for _, group in enumerate(page_groups):
    for _, page in enumerate(group):
        for _, asset in enumerate(page["data"]):
            # If the item is on sale OR if excluding offsale assets is off in the config
            if ("price" in asset) or not exclude_offsale:
                assets.append(asset)