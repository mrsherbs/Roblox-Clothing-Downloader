import json
import time
import requests
import configparser

config_file = "config.ini"
config = configparser.ConfigParser()
config.read(config_file)

# Wait time for every web request, necessary because of how archaic and undocumented the Roblox API is
wait_time = float(config.get("wait", "base"))
ratelimit_wait = float(config.get("wait", "ratelimit"))


# Takes an inputted string, and will return either True, False, or None
def string_to_bool(value):
    if value == "True" or value == "true":
        return True
    elif value == "False" or value == "false":
        return False
    else:
        return None


# Convert each item in a list to a type, (ex: str to int)
def convert_list(li: list, convert_to: type):
    for count, value in enumerate(li):
        li[count] = convert_to(value)

    return li


# From a group id and an optional starting cursor param, download every page of a groups assets recursively
def get_pages(group, **kwargs):
    # Optional cursor param, if there is a cursor the function will download that page and every page after it instead
    start_cursor = kwargs.get("cursor", None)

    all_pages = []
    print("Getting pages for group ID: " + str(group))

    # Define another function inside the get_pages() function to get every page
    def recurse_pages(group_id, **kwargs_recurse):
        time.sleep(wait_time)
        # Get the cursor param
        cursor = kwargs_recurse.get("cursor", None)
        catalog_url = "https://catalog.roblox.com/v1/search/items/details?Category=3&CreatorType=2&IncludeNotForSale=true&Limit=30&CreatorTargetId=" + str(
            group_id)

        # If there is a cursor, change the catalog link to include the cursor
        if cursor:
            catalog_url = catalog_url + "&cursor=" + cursor

        resp = requests.get(catalog_url)
        text = resp.text
        data = json.loads(text)

        # If there is an error, return, since there is no way to get the next cursor after this
        if "errors" in data:
            # Print out the error data
            print(data)
            return False
        else:
            # Save the page to the list
            all_pages.append(data)
            print("Page of assets saved")

            # Get the next cursor from the page
            next_cursor = data["nextPageCursor"]
            if next_cursor:
                return recurse_pages(group_id, cursor=next_cursor)
            else:
                return True

    # If there is a starting cursor, use it as an argument for the recursive function
    if start_cursor:
        success = recurse_pages(group, cursor=start_cursor)
    else:
        success = recurse_pages(group)

    if success:
        print("Pages have been saved")
        return [all_pages, True]
    else:
        print("All pages could not be downloaded")
        # We return the all_pages list since it can be used to run this function again from the next page
        return [all_pages, False]


# Waits 45 seconds for the roblox rate limit to end
def wait_45():
    print("Retrying in 45 seconds...")
    time.sleep(45)


# Converts a catalog url or asset ID to asset delivery link
def to_asset_delivery_url(to_be_converted):
    converted = str(to_be_converted).replace("https://www.roblox.com/catalog/", "")
    converted = converted.replace("http://www.roblox.com/asset/?id=", "")
    converted = converted.split("/")
    return "https://assetdelivery.roblox.com/v2/asset?id=" + converted[0]


# Returns an asset download link from the inputted link or asset ID
def get_asset_download_link(asset):
    converted = to_asset_delivery_url(asset)
    resp = requests.get(converted)
    text = resp.text
    data = json.loads(text)

    if "errors" in data:
        print("Could not be saved")
        print(data)
        return None

    return data["locations"][0]["location"]


def download(url):
    request = requests.get(url)
    return request.content
