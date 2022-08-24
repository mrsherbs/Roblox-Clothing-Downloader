import configparser
import os
import cv2
import functions

config_file = "config.ini"
config = configparser.ConfigParser()
config.read(config_file)

directory = save_directory = config.get("background-replacer", "directory")
add_logo = functions.string_to_bool(config.get("background-replacer", "add_logo"))
if add_logo:
    logo_image = cv2.imread('logo.png', cv2.IMREAD_UNCHANGED)
    logo = cv2.resize(logo_image, (100, 100))
background = functions.convert_list(config.get("background-replacer", "background_color").split(","), int)

# Take a template image and replace the original posters background, to erase any watermarks.

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f) and not filename == ".gitkeep":
        image = cv2.imread(f, cv2.IMREAD_UNCHANGED)

        # Remove top section
        image = functions.remove_pixels(585, 8, 0, 0, image, background)

        # Removes top left section
        image = functions.remove_pixels(231, 74, 0, 0, image, background)

        # Removes top right section
        image = functions.remove_pixels(226, 74, 359, 0, image, background)

        # Removes left section
        image = functions.remove_pixels(165, 355, 0, 0, image, background)

        # Removes section to the right of the last section
        image = functions.remove_pixels(217, 153, 0, 202, image, background)

        # Removes middle section
        image = functions.remove_pixels(27, 291, 281, 268, image, background)

        # Removes bottom left section
        image = functions.remove_pixels(217, 76, 0, 483, image, background)

        # Removes middle left section
        image = functions.remove_pixels(19, 483, 0, 0, image, background)

        # Removes bottom section
        image = functions.remove_pixels(580, 10, 0, 549, image, background)

        # Removes bottom right section
        image = functions.remove_pixels(213, 76, 372, 483, image, background)

        # Removes upper right section
        image = functions.remove_pixels(226, 66, 359, 202, image, background)

        # Removes lower right section
        image = functions.remove_pixels(213, 66, 372, 289, image, background)

        # Removes the right other section thing
        image = functions.remove_pixels(30, 128, 555, 74, image, background)

        # Why did I write the code like this
        image = functions.remove_pixels(14, 87, 217, 202, image, background)

        image = functions.remove_pixels(368, 21, 217, 268, image, background)

        image = functions.remove_pixels(15, 128, 570, 355, image, background)

        x_offset = y_offset = 25
        if add_logo:
            image[y_offset:y_offset + logo.shape[0], x_offset:x_offset + logo.shape[1]] = logo
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imwrite(directory + "\\" + filename, image)
        print("Saved: " + filename)
