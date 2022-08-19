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

# Wait time for every web request, necessitated by the archaic, undocumented Roblox API
wait_time = float(config.get("wait", "base"))

page_groups = []
assets = []
xml_content = []

# Download every page from these group IDs
# Each page contains a list of assets and info on them
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
                functions.wait_45()
                success = functions.get_pages(group_id, cursor=cursor_left_off_on)
        else:
            # If it didn't download any pages, restart without adding a cursor argument
            functions.wait_45()
            success = functions.get_pages(group_id)
    else:
        # If it finished without any issue, add it to the pages list
        page_groups.append(success[0])

# From every page, get every asset's info and add it to a list
for group in page_groups:
    for page in group:
        for asset in page["data"]:
            # If the item is on sale or if excluding offsale assets is set to False
            # If the item is not a T-Shirt
            if ("price" in asset or not exclude_offsale) and (not asset["assetType"] == 2):
                # If the asset is a shirt
                if asset["assetType"] == 11:
                    if include_favorite_count:
                        asset["name"] = asset["name"] + " [+]" + " [" + str(asset["favoriteCount"]) + "]"
                    else:
                        asset["name"] = asset["name"] + " [+]"
                # If the asset is a pair of pants
                elif include_favorite_count:
                    asset["name"] = asset["name"] + " [-]" + " [" + str(asset["favoriteCount"]) + "]"
                else:
                    asset["name"] = asset["name"] + " [-]"

                assets.append(asset)

print(str(len(assets)) + " assets to be downloaded")

# Get the XML file containing the download link for an asset's template
for asset in assets:
    asset_name = asset["name"]
    asset_id = asset["id"]
    time.sleep(wait_time)
    xml_link = functions.get_asset_download_link(asset_id)

    if xml_link:
        print("XML file saved")
        xml_content.append([functions.download(xml_link), asset_name])
    else:
        # Basically, repeat wait until Roblox stops ratelimiting
        while True:
            functions.wait_45()
            xml_link = functions.get_asset_download_link(asset_id)
            if xml_link:
                xml_content.append([functions.download(xml_link), asset_name])
                break
