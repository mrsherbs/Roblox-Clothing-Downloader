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

# Download every page from these group IDs
# Each page contains a list of assets and info on them
all_pages = []
for count, group_id in enumerate(group_ids):
    success = functions.get_pages(group_ids[count])
    # If downloading the pages led to an error
    if not success[1]:
        # The function returns all the pages it downloaded before it stopped running, so we save those
        all_pages.append(success[0])
        # Check if the function downloaded any pages before returning
        if 0 < len(all_pages[-1]):
            # if it did, get the last pages cursor and use that as an argument, to start again where it ended
            cursor_left_off_on = all_pages[-1][-1]["nextPageCursor"]
            if cursor_left_off_on:
                # Wait for the rate limit to end (Should be 45~ seconds)
                print("Retrying in 45 seconds...")
                time.sleep(45)
                success = functions.get_pages(group_ids[count], cursor=cursor_left_off_on)
        else:
            # If it didn't download any pages, restart without adding a cursor argument
            print("Retrying in 45 seconds...")
            time.sleep(45)
            success = functions.get_pages(group_ids[count])
    else:
        # If it stopped without any issue, add it to the pages list
        all_pages.append(success[0])