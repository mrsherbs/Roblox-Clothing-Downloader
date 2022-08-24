import configparser
import time
import uuid
import xml.etree.ElementTree as ElementTree
import functions

config_file = "config.ini"
config = configparser.ConfigParser()
config.read(config_file)

# First it uses a function that, using the group's id, downloads a page of assets. 
# It then uses that page's cursor to recursively download the next page until there are no more pages left. 
# We then add all the assets to a list, and return that list.
# From there, we use that list to download all the asset's XML files which all contain a download link to the template file. 
# We can then use that link to download the asset's template file.

# Downloader settings
save_directory = config.get("downloader", "save_directory")
group_ids = functions.convert_list(config.get("downloader", "group_ids").split(","), int)
exclude_offsale = functions.string_to_bool(config.get("downloader", "exclude_offsale"))
include_favorite_count = functions.string_to_bool(config.get("downloader", "include_favorites"))

# Wait time for every web request, necessitated by the archaic, undocumented Roblox API
wait_time = functions.wait_time

# List for storing page groups
page_groups = []
# List for storing all the assets
assets = []
# List for storing all the assets XML files
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
                functions.wait_ratelimit()
                success = functions.get_pages(group_id, cursor=cursor_left_off_on)
        else:
            # If it didn't download any pages, restart without adding a cursor argument
            functions.wait_ratelimit()
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

print("Downloading asset's XML files")
# Get the XML file containing the download link for an asset's template
for asset in assets:
    time.sleep(wait_time/4)
    asset_name = asset["name"]
    asset_id = asset["id"]
    # Get the XML files link, which contains the download link for the asset's template
    xml_link = functions.get_asset_download_link(asset_id)

    if xml_link:
        xml_content.append([functions.download(xml_link), asset])
    else:
        # Basically, repeat wait until Roblox stops ratelimiting
        while True:
            functions.wait_ratelimit()
            xml_link = functions.get_asset_download_link(asset_id)
            if xml_link:
                xml_content.append([functions.download(xml_link), asset])
                break

    print("Downloading XML file: " + asset["name"])

print("XML files downloaded")
print("Downloading templates")

# Get the download URLs from the XMLs and download the assets
for xml in xml_content:
    time.sleep(wait_time/4)
    xml_file = xml[0]
    asset_name = xml[1]["name"]
    root = ElementTree.fromstring(xml[0])
    # Root --> Item Class --> Properties --> Content Name --> URL --> URL Text
    template_link = root[2][0][0][0].text

    if template_link:
        download_link = functions.get_asset_download_link(template_link)
        if download_link:
            if not asset_name == "[Content Deleted]":
                functions.save_file(save_directory, download_link, str(asset_name), ".png")
            else:
                # If the asset name is deleted, generate a random name for the file
                functions.save_file(save_directory, download_link, str(uuid.uuid4()), ".png")
                print("Template saved, asset name was Content Deleted")
        else:
            print("Template could not be downloaded")
    else:
        print("XML does not contain a url. Template could not be downloaded")
