# Roblox-Clothing-Tools
Automation tools for Roblox clothing assets

# Features
* Automatically download clothing assets from Roblox
* Remove clothing template backgrounds and add custom logos to them
* Upload downloaded assets to Roblox (WIP, not complete)

# Usage
Change settings in the config.ini file, then run the clothing-downloader program.
Optionally, move the downloaded templates to the designated background replacer direcotry. 
Them, run the background-remover program to replace the template backgrounds.

# How this works
First it uses a function that, using the group's id, downloads a page of assets. 
It then uses that page's cursor to recursively download the next page until there are no more pages left. 
We then add all the assets to a list, and return that list.
From there, we use that list to download all the asset's XML files which all contain a download link to the template file. 
We can then use that link to download the asset's template file.

The background replacer will take a template image and replace the original posters background, to erase any watermarks.
