# ============================================================================ #
#
#                           Copyright (c) 2020-2023
#                               Sebastian Thiem
#
#                 Permission is hereby granted, free of charge,
#                to any person obtaining a copy of this software
#              and associated documentation files (the "Software"),
#                 to deal in the Software without restriction,
#                 including without limitation the rights to
#            use, copy, modify, merge, publish, distribute, sublicense,
#                     and/or sell copies of the Software,
#         and to permit persons to whom the Software is furnished to do so,
#                    subject to the following conditions:
#
#     The above copyright notice and this permission notice shall be included
#             in all copies or substantial portions of the Software.
#
#         THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#               EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
#                      THE WARRANTIES OF MERCHANTABILITY,
#             FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#             IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
#               LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#              WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#            ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
#                 OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ============================================================================ #
#
# Description:  Refresh/populate the server video metadata files by
#               extracting information from database websites.
#                  - MAL
#                  - Wikipedia
#
# ============================================================================ #
import datetime
import os
import re
import configparser

from libs.web_scraping import check_for_config_issues, load_meta_data, \
    determine_missing_required_params, store_meta_data, \
    update_meta_data, download_my_anime_list, \
    download_wikipedia, download_imdb


def is_valid_video_title(title: str) -> bool:
    """Simple check to see if the title is fitting the expected format.
    So far that just includes checking to see if it is a special windows file.

    Args:
        title (str): Title of the folder.

    Returns:
        bool: True if the folder is a media title, false if not.
    """
    return not title.startswith("$")


def download_missing_video_data():
    """
        Loop through the video metadata files and verify that 
        the necessary parameters are present.
        If they are not extract the information from the web.
    """

    def update_no_overwrite(dict_dst: dict, dict_src: dict) -> dict:
        for key, val in dict_src.items():
            if key not in dict_dst:
                dict_dst[key] = val
        return dict_dst

    # Load in the config data
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Ensure that the required parameters are present and
    # defined correctly
    is_valid_config = check_for_config_issues(config,
                                              [
                                                  ("folders", "FolderVideo"), ("folders",
                                                                               "ThumbnailCacheVideo"),
                                                  ("webscraping", "RequiredMetadataVideo"), (
                                                      "webscraping", "UserAgent")
                                              ],
                                              [
                                                  ("folders", "FolderVideo"), ("folders",
                                                                               "ThumbnailCacheVideo")
                                              ])
    if not is_valid_config:
        print("Exiting...")
        return

    required_metadata = config["webscraping"]["RequiredMetadataVideo"].split(
        ",")

    db_connection_str = os.getenv('DB_ADDRESS')

    # Loop through each Video Folder in the Maga Directory
    # Check each metadata file for the required data
    # For each video that does not have all the required data
    # log to console, go online to find the data, update the metadata file.
    data_dir_video = config["folders"]["FolderVideo"]
    video_list = os.listdir(data_dir_video)
    incomplete_metadata_set = set()
    for title in video_list:

        if not is_valid_video_title(title):
            continue

        media_folder = data_dir_video+title

        if not os.path.isdir(media_folder):
            continue

        # initialize the meta data file
        meta_data = load_meta_data("video", title, db_connection_str)

        is_update = len(meta_data) > 0

        # If there are missing parameters go through an aquire them
        missing_params = determine_missing_required_params(meta_data,
                                                           required_metadata)
        if 0 < len(missing_params):
            print(title)
            print(f"WARNING! Cache is missing: [{', '.join(missing_params)}].")

            # Title is  always the name of the folder the media is in
            meta_data['title'] = title

            # Get the thumbnail, and store the path in the metadata
            # NOTE: This is a true backup. We will attempt to
            #       download thumbnails and overwrite this one.
            # Remove certain characters that shouldnt be in a filename
            titleClean = re.sub(r"[?\/\\:]", "", title)
            thumbnail_addr = config["folders"]["ThumbnailCacheVideo"] + \
                titleClean + ".jpg"

            # Read from MAL if we have not tried that yet
            if 'visited_mal' not in meta_data.keys() or meta_data["visited_mal"] == False:
                print("Querying MAL...")
                extracted_data = download_my_anime_list(
                    title,
                    None if os.path.exists(thumbnail_addr) else thumbnail_addr)
                if extracted_data:
                    meta_data = update_no_overwrite(meta_data, extracted_data)
                else:
                    meta_data["visited_mal"] = True

            # Read from MAL if we have not tried that yet
            if 'visited_wikipedia' not in meta_data.keys() or meta_data["visited_wikipedia"] == False:
                print("Querying Wikipedia...")
                extracted_data = download_wikipedia(
                    title,
                    None if os.path.exists(thumbnail_addr) else thumbnail_addr)
                if extracted_data:
                    meta_data = update_no_overwrite(meta_data, extracted_data)
                else:
                    meta_data["visited_wikipedia"] = True

            # Read from MAL if we have not tried that yet
            if 'visited_imdb' not in meta_data.keys() or meta_data["visited_imdb"] == False:
                print("Querying IMDB...")
                extracted_data = download_imdb(
                    title,
                    None if os.path.exists(thumbnail_addr) else thumbnail_addr)
                if extracted_data:
                    meta_data = update_no_overwrite(meta_data, extracted_data)
                else:
                    meta_data["visited_imdb"] = True

            # TODO: Read from AniDB

            # Log if we still don't have enough data after webscraping
            if 0 < len(determine_missing_required_params(meta_data, required_metadata)):
                print(
                    f"WARNING! We are still missing: [{', '.join(missing_params)}].")
                incomplete_metadata_set.add(
                    (title, ",".join(missing_params), os.path.exists(thumbnail_addr)))

            if "dateAdded" not in meta_data or not meta_data["dateAdded"]:
                meta_data["dateAdded"] = datetime.datetime.now()

            # Stash the metadata retrieved
            if is_update:
                update_meta_data("video", title, meta_data, db_connection_str)
            else:
                meta_data["_id"] = title
                store_meta_data("video", meta_data, db_connection_str)

    # Communicate the status
    # NOTE: We package a lot of info in a tuple, and sort the titles before
    #       printing out
    if incomplete_metadata_set:
        incomplete_metadata_list = list(incomplete_metadata_set)
        incomplete_metadata_list.sort(key=lambda x: x[0])
        print("Missing data on the following series:")
        for title, missing_params, if_thumbnail_on_file in incomplete_metadata_list:
            print(f"  - {title}")
            if not if_thumbnail_on_file:
                print("     - Thumbnail Is Not On File")
            for param in missing_params.split(","):
                print(f"     - {param}")
    else:
        print(f"All {len(video_list)} video metadata files are up to date.")


if __name__ == "__main__":
    if "DB_ADDRESS" not in os.environ:
        print("DB_ADDRESS was not set; required for this script.")
        exit(1)

    download_missing_video_data()
