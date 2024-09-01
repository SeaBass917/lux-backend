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
# Description:  Refresh/populate the server manga metadata files by
#               extracting information from database websites.
#                  - MangaUpdates
#
# ============================================================================ #
import datetime
import os
import shutil
import re
import configparser

from libs.web_scraping import check_for_config_issues, load_meta_data, \
    determine_missing_required_params, store_meta_data, \
    update_meta_data, download_manga_updates


def is_valid_manga_title(title: str) -> bool:
    """Simple check to see if the title is fitting the expected format.
    So far that just includes checking to see if it is a special windows file.

    Args:
        title (str): Title of the folder.

    Returns:
        bool: True if the folder is a media title, false if not.
    """
    return not title.startswith("$")


def get_manga_cover_art(manga_dir: str, caching_addr: str):
    """
        Get the first image from the manga and use it as a cover image.
        Store the image in the specified path.
    """

    # If the image is already there there is nothing to do
    if os.path.exists(caching_addr):
        return

    # Get the first volume
    vols = os.listdir(manga_dir)
    if len(vols) == 0:
        return
    vols.sort()
    vol_0 = vols[0]
    dir_vol_0 = manga_dir+vol_0
    if not os.path.isdir(dir_vol_0):
        return

    # Get the first page of the first volume
    pages = os.listdir(dir_vol_0)
    if len(pages) == 0:
        return
    pages.sort()
    page_0 = pages[0]
    path_page_0 = f"{dir_vol_0}/{page_0}"

    # Use the first page as a thumbnail
    shutil.copy(path_page_0, caching_addr)


def download_missing_manga_data():
    """
        Loop through the manga metadata files and verify that the necessary parameters are present.
        If they are not extract the information from the web.
    """

    # Load in the config data
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Ensure that the required parameters are present and
    # defined correctly
    is_valid_config = check_for_config_issues(config,
                                              [
                                                  ("folders", "FolderManga"), ("folders",
                                                                               "ThumbnailCacheManga"),
                                                  ("webscraping", "RequiredMetadataManga"), (
                                                      "webscraping", "UserAgent")
                                              ],
                                              [
                                                  ("folders", "FolderManga"), ("folders",
                                                                               "ThumbnailCacheManga")
                                              ])
    if not is_valid_config:
        print("Exiting...")
        return

    required_metadata = config["webscraping"]["RequiredMetadataManga"].split(
        ",")

    db_connection_str = os.getenv('DB_ADDRESS')

    # Loop through each Manga Folder in the Manga Directory
    # Check each metadata file for the required data
    # For each manga that does not have all the required data
    # log to console, go online to find the data, update the metadata file.
    data_dir_manga = config["folders"]["FolderManga"]
    manga_list = os.listdir(data_dir_manga)
    incomplete_metadata_set = set()
    for title in manga_list:

        if not is_valid_manga_title(title):
            continue

        manga_folder = data_dir_manga+title

        if not os.path.isdir(manga_folder):
            continue

        # initialize the meta data file
        meta_data = load_meta_data("manga", title, db_connection_str)

        is_update = len(meta_data) > 0

        # If there are missing parameters go through an acquire them
        missing_params = determine_missing_required_params(meta_data,
                                                           required_metadata)
        if 0 < len(missing_params):
            print(title)
            print(f"WARNING! Cache is missing: [{', '.join(missing_params)}].")

            # Title is  always the name of the folder the manga is in
            meta_data['title'] = title

            # Get the thumbnail, and store the path in the metadata
            # NOTE: This is a true backup. We will attempt to
            #       download thumbnails and overwrite this one.
            # Remove certain characters that shouldnt be in a filename
            titleClean = re.sub(r"[?\/\\:]", "", title)
            thumbnail_addr = config["folders"]["ThumbnailCacheManga"] + \
                titleClean + ".jpg"
            get_manga_cover_art(manga_folder, thumbnail_addr)

            # Read from MangaUpdates if we have not tried that yet
            if 'visited_mangaupdates' not in meta_data.keys() or meta_data["visited_mangaupdates"] == False:
                print("Querying MangaUpdates...")
                extracted_data = download_manga_updates(title, thumbnail_addr)
                if extracted_data:
                    meta_data.update(extracted_data)
                else:
                    meta_data["visited_mangaupdates"] = True

            # TODO: Read from MAL or other sources next

            # Log if we still don't have enough data after webscraping
            if 0 < len(determine_missing_required_params(meta_data, required_metadata)):
                print(
                    f"WARNING! We are still missing: [{', '.join(missing_params)}].")
                incomplete_metadata_set.add(title)

            if "dateAdded" not in meta_data or not meta_data["dateAdded"]:
                meta_data["dateAdded"] = datetime.datetime.now()

            # Stash the metadata retrieved
            if is_update:
                update_meta_data("manga", title, meta_data, db_connection_str)
            else:
                meta_data["_id"] = title
                store_meta_data("manga", meta_data, db_connection_str)

    # Communicate the status
    if incomplete_metadata_set:
        print("Missing data on the following series:\n  - " +
              "\n  - ".join(incomplete_metadata_set))
    else:
        print(f"All {len(manga_list)} manga metadata files are up to date.")


if __name__ == "__main__":
    if "DB_ADDRESS" not in os.environ:
        print("DB_ADDRESS was not set; required for this script.")
        exit(1)

    download_missing_manga_data()
