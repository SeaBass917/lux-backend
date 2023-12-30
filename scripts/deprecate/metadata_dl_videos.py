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
#                  - AniDB
#                  - Wikipedia
#
# ============================================================================ #
import os
import shutil
import re
import configparser

from libs.web_scraping import check_for_config_issues, load_meta_data, \
    determine_missing_required_params, store_meta_data, \
    get_top_url, get_soup, get_image, fmt_check


def extract_anidb(title: str, thumbnail_addr: str):
    """
        Extract the information from an aniDB webpage. 
        Takes the url of the page as an arguement.
    """

    metaData = {}

    for url in googlesearch.search(title + " anidb", num=1, stop=1, pause=1):

        if re.match(r"https:\/\/anidb\.net\/anime\/\d+", url):

            print(f"Grabbing data from AniDB: '{url}'")
            # soup = getSoup(url)
            soup = None
            if soup:
                metaData["visited_AniDB"] = True

                # Extract what we need
                e0 = soup.find_all("label", {"itemprop": "alternateName"})
                if e0 and 1 < len(e0):
                    txt = e0[1].get_text()
                    if fmtCheck(txt, 'title-jp'):
                        metaData['title-jp'] = txt

                e0 = soup.find("table", {"class": "staff"})
                if e0:
                    e1 = e0.find_all("a")
                    if e1 and 0 < len(e1):
                        txt = e1[-1].get_text()
                        if fmtCheck(txt, 'studio'):
                            metaData['staff'] = txt

                e0 = soup.find("tr", {"class": "tags"})
                if e0:
                    e1 = e0.find_all("span", {"itemprop": "genre"})
                    if e1:
                        txt = ", ".join([span.get_text() for span in e1])
                        if fmtCheck(txt, 'tags'):
                            metaData['tags'] = txt

                e0 = soup.find("span", {"itemprop": "numberOfEpisodes"})
                if e0:
                    txt = e0.get_text()
                    if fmtCheck(txt, 'numberOfEpisodes'):
                        metaData['numEpisodes'] = txt

                e0 = soup.find("span", {"itemprop": "startDate"})
                if e0:
                    startDate = e0.get_text()
                    if startDate != "?":
                        if fmtCheck(startDate, 'date'):
                            [startDay, startMonth,
                                startYear] = startDate.split(".")
                            metaData['dayStart'] = startDay
                            metaData['monthStart'] = startMonth
                            metaData['yearStart'] = startYear

                e0 = soup.find("span", {"itemprop": "endDate"})
                if e0:
                    endDate = e0.get_text()
                    if endDate != "?":
                        if fmtCheck(endDate, 'date'):
                            [endDay, endMonth, endYear] = endDate.split(".")
                            metaData['dayEnd'] = endDay
                            metaData['monthEnd'] = endMonth
                            metaData['yearEnd'] = endYear

                e0 = soup.find("div", {"itemprop": "description"})
                if e0:
                    # NOTE: We replace newlines with --- since its going in an ini file
                    txt = e0.get_text().replace("\n", "---")
                    if fmtCheck(txt, 'description'):
                        metaData['description'] = txt

                # Cache the image for thumbnails
                e0 = soup.find("img", {"itemprop": "image"})
                if e0:
                    icon_url = e0['src']

                    # Cache the data
                    if icon_url:
                        local_cache_addr = DATA_DIR+THUMBNAIL_CACHE_VIDEOS
                        if not os.path.exists(local_cache_addr):
                            os.makedirs(local_cache_addr)

                        # Remove certain characters that shouldnt be in a filename
                        titleClean = re.sub(title, r"[?\/\\]", "")

                        try:
                            urlretrieve(
                                icon_url, local_cache_addr+titleClean+".png")

                            # Save the location of the icon
                            metaData['iconAddr'] = THUMBNAIL_CACHE_VIDEOS + \
                                titleClean+".png"

                        except HTTPError:
                            print(
                                f"HTTP connection was denied to '{icon_url}'.")
                        except:
                            print(f"Unknown Error in accessing '{icon_url}'.")

            else:
                print("\tERROR! Failed to access page. No data extracted.")
        else:
            print(f"\tWarning. Unsure about anidb link: '{url}'. Skipping.")

    # print(metaData)
    return metaData


def extract_wikipedia(title: str, thumbnail_addr: str):
    """
        Extract the information from an Wikipedia webpage. 
        Takes the url of the page as an arguement.
    """

    # Map for determining what data we care about and where to put it
    header_to_key = {
        "japanese": "jp-title",
        "directed": "director",
        "screenplay": "screenplay",
        "written": "writer",
        "produced": "producer",
        "cinematography": "cinematographer",
        "edited": "editor",
        "distributed": "studio",
        "date": "",  # This break down into a few keys
        "running time": "runtime",
        "countr": "country",
        "language": "language",
        "budget": "budget",
        "box office": "boxOffice",
        "seasons": "numSeasons",
        "episodes": "numEpisodes",
        "release": "",  # This break down into a few keys
    }

    metaData = {}

    for url in googlesearch.search(title + " wikipedia", num=1, stop=1, pause=1):

        if url.startswith("https://en.wikipedia.org/wiki/"):

            print(f"Grabbing data from Wiki Page: '{url}'")
            # soup = getSoup(url)
            soup = getSoupLocal(
                "local_sites/Léon_ The Professional - Wikipedia.html")
            if soup:
                metaData["visited_Wikipedia"] = True

                # Grab the right panel of meta-data
                e0 = soup.find("table", {"class": "infobox vevent"})
                if e0:
                    e1 = e0.find_all("tr")
                    if e1:

                        # For each row in the data box
                        for tr in e1:
                            tr_children = [child for child in tr.children]

                            # See if it is the thumbnail
                            e_img = tr.find("td", {"class": "infobox-image"})
                            if e_img:
                                img = e_img.find("img")
                                print(img)

                            elif 2 == len(tr_children):
                                th = tr_children[0]
                                td = tr_children[1]

                                if th.name == "th" and td.name == "td":
                                    for head in header_to_key.keys():
                                        if head in th.string.lower():
                                            print(tr)

                # Cache the image for thumbnails
                e0 = soup.find("img", {"itemprop": "image"})
                if e0:
                    icon_url = e0['src']

                    # Cache the data
                    if icon_url:
                        local_cache_addr = DATA_DIR+THUMBNAIL_CACHE_VIDEOS
                        if not os.path.exists(local_cache_addr):
                            os.makedirs(local_cache_addr)

                        # Remove certain characters that shouldnt be in a filename
                        titleClean = re.sub(title, r"[?\/\\]", "")

                        try:
                            urlretrieve(
                                icon_url, local_cache_addr+titleClean+".png")

                            # Save the location of the icon
                            metaData['iconAddr'] = THUMBNAIL_CACHE_VIDEOS + \
                                titleClean+".png"

                        except HTTPError:
                            print(
                                f"HTTP connection was denied to '{icon_url}'.")
                        except:
                            print(f"Unknown Error in accessing '{icon_url}'.")

            else:
                print("\tERROR! Failed to access page. No data extracted.")
        else:
            print(f"\tWarning. Unsure about anidb link: '{url}'. Skipping.")

    # print(metaData)
    return metaData


def download_missing_video_data():
    """
        Loop through the video metadata files and verify that the necessary parameters are present.
        If they are not extract the information from the web.
    """

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

    # Loop through each Video Folder in the Maga Directory
    # Check each metadata file for the required data
    # For each video that does not have all the required data
    # log to console, go online to find the data, update the metadata file.
    data_dir_video = config["folders"]["FolderVideo"]
    video_list = os.listdir(data_dir_video)
    incomplete_metadata_set = set()
    for title in video_list:

        video_folder = data_dir_video+title
        meta_file_path = f"{video_folder}/info.meta"

        if not os.path.isdir(video_folder):
            continue

        # initialize the meta data file
        meta_data = load_meta_data(meta_file_path)

        # If there are missing parameters go through an aquire them
        missing_params = determine_missing_required_params(meta_data,
                                                           required_metadata)
        if 0 < len(missing_params):
            print(title)
            print(f"WARNING! Cache is missing: [{', '.join(missing_params)}].")

            # Title is  always the name of the folder the video is in
            meta_data['title'] = title

            # Read from VideoUpdates if we have not tried that yet
            if 'visited_videoupdates' not in meta_data.keys() or meta_data["visited_videoupdates"] == False:
                print("Querying VideoUpdates...")
                extracted_data = download_video_updates(title, thumbnail_addr)
                if extracted_data:
                    meta_data.update(extracted_data)

            # TODO: Read from MAL or other sources next

            # Log if we still don't have enough data after webscraping
            if 0 < len(determine_missing_required_params(meta_data, required_metadata)):
                print(
                    f"WARNING! We are still missing: [{', '.join(missing_params)}].")
                incomplete_metadata_set.add(title)

        # Stash the metadata retrieved
        store_meta_data("video", meta_data)

    # Communicate the status
    if incomplete_metadata_set:
        print("Missing data on the following series:\n  " +
              "\n  ".join(incomplete_metadata_set))
    else:
        print(f"All {len(video_list)} video metadata files are up to date.")


if __name__ == "__main__":
    download_missing_video_data()
