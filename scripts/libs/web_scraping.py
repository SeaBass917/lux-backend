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
# Description:  Library for common webscraping functions used by all
#               media types in this program.
#
# ============================================================================ #
from os.path import isdir, isfile

import googlesearch
import re
from time import sleep
import pymongo

from bs4 import BeautifulSoup

from urllib.error import HTTPError
from urllib.request import urlopen, urlretrieve, Request


def extract_year(text: str) -> str | None:
    """Extract a year from a string that contains a date or dates.
    Very specific utility function for this DB.
    We typically just want the year, so this comes up a lot

    Args:
        text (str): Text containing one or more date strings.

    Returns:
        str | None: The first year in that string.
    """

    date_match = re.search(
        r"[a-zA-Z]+ [0-9][0-9]?, [0-9][0-9][0-9][0-9]", text)
    if date_match:
        group = date_match.group()
        if group:
            return group.split(", ")[1]

    date_match = re.search(
        r"[a-zA-Z]+ [0-9][0-9]? [0-9][0-9][0-9][0-9]", text)
    if date_match:
        group = date_match.group()
        if group:
            return group.split(" ")[2]

    date_match = re.search(
        r"[0-9][0-9]? [a-zA-Z]+ [0-9][0-9][0-9][0-9]", text)
    if date_match:
        group = date_match.group()
        if group:
            return group.split(" ")[2]

    return None


def check_for_config_issues(config, required_parameters=[], folder_parameters=[]):
    """Check that the config passed contains all the necessary information,
    and that no folders are missing, etc...

    Returns
    -------
    True IF the config is valid ELSE False
    """
    config_valid = True

    # Check that required params are present
    for category, parameter in required_parameters:
        if parameter not in config[category]:
            config_valid = False
            print(
                f"Required paramter \"{parameter}\" under category \"{category}\" is missing from config.ini")

    # Check that the folders exist
    for category, parameter in folder_parameters:
        folder = config[category][parameter]
        if not isdir(folder):
            config_valid = False
            print(f"{parameter} configured as {folder} , which does not exist.")
            print(
                "Please set up folders per the installation instructions before starting server.")

    return config_valid


def load_meta_data(db_name: str, title: str, connection_str: str) -> dict:
    """
        Loads the metadata from the given address.
        Returns the data in a dicitonary.
    """

    db = pymongo.MongoClient(connection_str)
    db_metadata = db["mediaMetadata"]
    collection = db_metadata[db_name]

    metadata = collection.find_one({"_id": title})

    db.close()

    return metadata if metadata else {}


def store_meta_data(db_name: str, meta_data: dict, connection_str: str):
    """
        Formats 'meta_data' dictionary as an ini file
        and stores it in 'address'
    """

    db = pymongo.MongoClient(connection_str)
    db_metadata = db["mediaMetadata"]
    collection = db_metadata[db_name]

    collection.insert_one(meta_data)

    db.close()


def update_meta_data(db_name: str, title: str, meta_data: dict, connection_str: str):
    """
        Formats 'meta_data' dictionary as an ini file
        and stores it in 'address'
    """

    db = pymongo.MongoClient(connection_str)
    db_metadata = db["mediaMetadata"]
    collection = db_metadata[db_name]

    collection.update_one({"_id": title}, {"$set": meta_data})

    db.close()


def determine_missing_required_params(meta_data: dict, required_params: list):
    """Check that the requried parameters are stored in the metadata.
    NOTE: iconAddr is an implied required paramater for all media types.
    """

    # Search for missing parameters
    missing_params = set()
    for key in required_params:
        if key not in meta_data.keys() or meta_data[key] == "":
            missing_params.add(key)

    return missing_params


def get_top_url(search_query: str) -> str:
    """Utility for getting the first URL result from a google search query."""
    urls = googlesearch.search(search_query, num_results=1, timeout=5)
    urls = [url for url in urls]
    return urls[0] if 0 < len(urls) else ""


def get_image(img_url: str, addr_store: str):
    """Utility for downloading an image.

    Returns
    -------
    True on successful download, ELSE False.
    """
    try:
        path, _ = urlretrieve(img_url, addr_store)
        if path == addr_store:
            return True
    except HTTPError:
        print(f"HTTP connection was denied to '{img_url}'.")
    except Exception as e:
        print(e)
        print(f"Unknown Error in accessing '{img_url}'.")

    return False


def fmt_check(parameter: str, parameterType: str):
    """
        Helper function: Does a check on the given parameter for formating issues

        Inputs:
            parameter - The parameter string itself
            parameterType - String describing the parameter class, TODO: Could be an enum.
    """

    if parameterType == 'title':
        return bool(re.match(r'[\w :;\\,\.\-]+', parameter))
    elif parameterType == 'title-jp':
        return bool(re.match(r'[一-龠]+|[ぁ-ゔ]+|[ァ-ヴー]+|[ａ-ｚＡ-Ｚ０-９]+|[々〆〤]+', parameter))
    elif parameterType == 'animator':
        return bool(re.match(r'[\w ,\.\-]+', parameter))
    elif parameterType == 'tags':
        return all([bool(re.match(r'[\w ,\-]+', tag)) for tag in parameter])
    elif parameterType == 'numberOfEpisodes':
        return bool(re.match(r'\d+', parameter))
    elif parameterType == 'date':
        return bool(re.match(r'\d\d\.\d\d\.\d\d\d\d', parameter))
    elif parameterType == 'description':
        return 0 < len(parameter)
    else:
        return True


def get_soup(url: str,
             user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7',
             delay=5.0):
    """
        Gets a accessable datastructure for the given webpage. 
        Returns None on failure.
    """
    print(
        f"Waiting {delay} seconds before requesting from server", end="", flush=True)
    for _ in range(int(delay)):
        sleep(1)
        print(".", end="", flush=True)
    print()

    try:
        req = Request(url, headers={'User-Agent': user_agent})
        html = urlopen(req).read()
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    except HTTPError:
        print(f"HTTP connection was denied to '{url}'.")
    except:
        print(f"Unknown Error in accessing '{url}'.")

    return None


def get_soup_local(addr: str):
    """
        Gets a accessable datastructure for the given local webpage. 
        Used for debugging.
        Returns None on failure.
    """

    with open(addr, mode='r', encoding='utf-8') as fp:
        html = fp.read()
        soup = BeautifulSoup(html, 'html.parser')
        return soup


def download_manga_updates(title: str, thumbnail_addr: str):
    """
        Extract the information from an MangaUpdates webpage. 
        Takes the url of the page as an arguement.
    """

    meta_data = {}

    # Get the top url when searching for "{Manga Title} MangaUpdates"
    url_top = get_top_url(title + " mangaupdates")

    # Check that the url seems valid.
    if not re.match(r"https:\/\/www\.mangaupdates\.com\/.+", url_top):
        print(
            f"\tWarning. Unsure about MangaUpdates link: '{url_top}'. Skipping MangaUpdates.")
        return {}

    print(f"Grabbing data from MangaUpdates: '{url_top}'")

    # Read the webpage from the top web result
    soup = get_soup(url_top)
    if not soup:
        print("\tERROR! Failed to access page. No data extracted.")

    # Get all the catagorical information
    data = {}
    categories = soup.find_all("div", {"class": "sCat"})
    for category in categories:
        data[category.get_text().split('\xa0')[0]] = category.find_next('div')

    # Download and cache the thumbnail
    if thumbnail_addr:
        if "Image" in data:
            imgs = data["Image"].findChildren('img')

            if 0 < len(imgs):
                icon_url = imgs[0]['src']
                if icon_url:
                    get_image(icon_url, thumbnail_addr)
            else:
                print("Can't find an image.")

    # TODO: Handle Newlines
    if "Description" in data:
        # NOTE: We replace newlines with --- since its going in an ini file
        #       And we need to grab the hidden div tht contains the full
        #       description
        desc_ele = data["Description"]
        txt = desc_ele.get_text().strip()
        if fmt_check(txt, 'description'):
            meta_data['description'] = txt

    if "Type" in data:
        txt = data["Type"].get_text().replace("\n", "")
        if fmt_check(txt, 'booktype'):
            meta_data['booktype'] = txt

    # TODO: Handle Newlines
    if "Associated Names" in data:
        txt = data["Associated Names"].get_text()
        for nameAlt in txt.split('\n'):
            if fmt_check(nameAlt, 'title-jp'):
                meta_data['title-jp'] = nameAlt
                break

    meta_data["nsfw"] = False
    if "Genre" in data:
        tag_links = data["Genre"].find_all("a")
        tags_list = [tag.get_text() for tag in tag_links][:-1]
        if fmt_check(tags_list, "tags"):
            meta_data["tags"] = tags_list

            if "Hentai" in tags_list or "Ecchi" in tags_list:
                meta_data["nsfw"] = True

    if "Author(s)" in data:
        txt = data["Author(s)"].get_text().replace("\n", "")
        if fmt_check(txt, 'author'):
            meta_data['author'] = txt

    if "Artist(s)" in data:
        txt = data["Artist(s)"].get_text().replace("\n", "")
        if fmt_check(txt, 'artist'):
            meta_data['artist'] = txt

    if "Year" in data:
        txt = data["Year"].get_text().replace("\n", "")
        if fmt_check(txt, 'year'):
            meta_data['yearstart'] = txt

    if "Original Publisher" in data:
        txt = data["Original Publisher"].get_text().replace("\n", "")
        if fmt_check(txt, 'publisher'):
            meta_data['publisher'] = txt

    if "Serialized In (magazine)" in data:
        txt = data["Serialized In (magazine)"].get_text().replace("\n", "")
        if fmt_check(txt, 'magazine'):
            meta_data['magazine'] = txt

    if "Licensed (in English)" in data:
        txt = data["Licensed (in English)"].get_text().replace(
            "\n", "").lower()
        if txt == 'yes':
            meta_data['englishlicense'] = True
        elif txt == 'no':
            meta_data['englishlicense'] = False

    meta_data["visited_mangaupdates"] = True

    return meta_data


def download_my_anime_list(title: str, thumbnail_addr: str):
    """
        Extract the information from an MAL webpage. 
        Takes the url of the page as an arguement.
    """

    meta_data = {}

    # Get the top url when searching for "{Anime Title} mal"
    url_top = get_top_url(title + " mal")

    # Check that the url seems valid.
    # e.g.
    # https://myanimelist.net/anime/6372/Higashi_no_Eden_Movie_I__The_King_of_Eden
    if not re.match(r"https:\/\/myanimelist\.net\/anime\/.+", url_top):
        print(f"\tWarning. Unsure about MAL link: '{url_top}'. Skipping MAL.")
        return {}

    print(f"Grabbing data from MAL: '{url_top}'")

    # Read the webpage from the top web result
    soup = get_soup(url_top)
    if not soup:
        print("\tERROR! Failed to access page. No data extracted.")

    # Get the description
    description_p = soup.find("p", {"itemprop": "description"})
    if description_p:
        txt = description_p.get_text().strip()
        if fmt_check(txt, 'description'):
            meta_data['description'] = txt

    # Get the "leftside" div that contains most of the metadata & image
    leftside = soup.find("div", {"class": "leftside"})
    if not leftside:
        print("\tERROR! MAL page doesn't have a leftside.")
        return

    # Download and cache the thumbnail
    if thumbnail_addr:
        thumbnail_img = leftside.find('img')
        if thumbnail_img:
            icon_url = thumbnail_img['data-src']
            if icon_url:
                get_image(icon_url, thumbnail_addr)
        else:
            print("Can't find an image.")

    # Get all the catagorical information from the left side
    # Format is <span>Key:</span> "Value"
    data = {}
    categories = leftside.find_all("div", {"class": "spaceit_pad"})
    for category in categories:
        if not category:
            continue

        # Get the text found in the key
        key_span = category.find("span")
        if not key_span:
            continue
        text_key = key_span.get_text()

        text_val = category.get_text()[len(text_key)+1:]

        data[text_key.strip()[:-1]] = text_val.strip()

    if "Type" in data:
        txt = data["Type"]
        if fmt_check(txt, 'datatype'):
            meta_data['datatype'] = txt

    if "Japanese" in data:
        txt = data["Japanese"]
        if fmt_check(txt, 'title-jp'):
            meta_data['title-jp'] = txt

    meta_data["nsfw"] = False
    if "Genres" in data:
        # Cleanup the multiple spaces + DOUBLE TEXT?? Why MAL???
        genre_list = data["Genres"].replace(" ", "").split(",")
        genre_list = [genre[int(len(genre)/2):] for genre in genre_list]

        if fmt_check(genre_list, "tags"):
            meta_data["tags"] = genre_list

            if "Hentai" in genre_list or "Ecchi" in genre_list:
                meta_data["nsfw"] = True

    if "Studios" in data:
        txt = data["Studios"].split(", ")[0]
        if fmt_check(txt, 'studio'):
            meta_data['studio'] = txt

    if "Aired" in data:
        eles = data["Aired"].split(" to ")
        txt = eles[0] if len(eles) == 1 else eles[1]

        eles = txt.split(", ")
        if 2 == len(eles):
            txt = eles[1]
            if fmt_check(txt, 'year'):
                meta_data['yearstart'] = txt

    if "Producers" in data:
        txt = data["Producers"].split(", ")[0]
        if fmt_check(txt, 'producer'):
            meta_data['producer'] = txt

    if "Licensors" in data:
        txt = data["Licensors"]
        if txt == 'None found, add some':
            meta_data['englishlicense'] = False
        else:
            meta_data['englishlicense'] = True

    meta_data["visited_mal"] = True

    return meta_data


def download_wikipedia(title: str, thumbnail_addr: str):
    """
        Extract the information from an WikiPedia webpage. 
        Takes the url of the page as an arguement.
    """

    meta_data = {}

    # Get the top url when searching for "{Title} wikipedia"
    url_top = get_top_url(title + " wikipedia")

    # Check that the url seems valid.
    # e.g.
    # https://en.wikipedia.org/wiki/Kill_Bill:_Volume_1
    if not re.match(r"https:\/\/en\.wikipedia\.org\/wiki\/.+", url_top):
        print(
            f"\tWarning. Unsure about Wikipedia link: '{url_top}'. Skipping Wikipedia.")
        return {}

    print(f"Grabbing data from Wikipedia: '{url_top}'")

    # Read the webpage from the top web result
    soup = get_soup(url_top)
    if not soup:
        print("\tERROR! Failed to access page. No data extracted.")

    # Get the "infobox" div that contains most of the metadata & image
    infobox = soup.find("table", {"class": "infobox"})
    if not infobox:
        print("\tERROR! Wikipedia page doesn't have a infobox.")
        return

    # Download and cache the thumbnail
    # if thumbnail_addr:
    #     thumbnail_img = infobox.find('img')
    #     if thumbnail_img:
    #         icon_url = thumbnail_img['src']
    #         if icon_url:
    #             get_image(icon_url, thumbnail_addr)
    #     else:
    #         print("Can't find an image.")

    # Get all the catagorical information from the left side
    # Format is <th>Key:</th> <td>Key:</td>
    data = {}
    categories = infobox.find_all("tr")
    for category in categories:
        if not category:
            continue

        # Get the text found in the key
        key_span = category.find("th")
        if not key_span:
            continue
        val_span = category.find("td")
        if not val_span:
            continue

        text_key = key_span.get_text()
        text_val = val_span.get_text()

        text_key = text_key.strip().replace(" ", "").replace("\n", "").lower()
        text_val = re.sub(r"\[[0-9]+\]$", "", text_val.strip())

        data[text_key] = text_val

    if "directedby" in data:
        txt = data["directedby"]
        if fmt_check(txt, 'director'):
            meta_data['director'] = txt

    # HACK Typos on the site
    studio_keys = ["productioncompany", "productioncompanies"]
    for key in studio_keys:
        if key in data:
            txt = data[key].split("\n")[0]
            if fmt_check(txt, 'studio'):
                meta_data['studio'] = txt

    date_keys = ["releasedate", "releasedates", "originalrelease"]
    date_txt = ""
    for date_key in date_keys:
        if date_key in data:
            date_txt = data[date_key].replace("\xa0", " ").replace("\n", " ")

    year_str = extract_year(date_txt)
    if year_str:
        if fmt_check(year_str, 'year'):
            meta_data['yearstart'] = year_str

    meta_data["visited_wikipedia"] = True

    return meta_data


def download_imdb(title: str, thumbnail_addr: str):
    """
        Extract the information from an IMDB webpage. 
        Takes the url of the page as an arguement.
    """

    meta_data = {}

    # Get the top url when searching for "{Title} imdb"
    url_top = get_top_url(title + " imdb")

    # Check that the url seems valid.
    # e.g.
    # https://www.imdb.com/title/tt0266697/
    if not re.match(r"https:\/\/www\.imdb\.com\/title\/.+", url_top):
        print(
            f"\tWarning. Unsure about IMDB link: '{url_top}'. Skipping IMDB.")
        return {}

    print(f"Grabbing data from IMDB: '{url_top}'")

    # Read the webpage from the top web result
    soup = get_soup(url_top)
    if not soup:
        print("\tERROR! Failed to access page. No data extracted.")

    # Get the description
    description = soup.find("p", {"data-testid": "plot"})
    if description:
        txt = description.get_text().strip()
        if fmt_check(txt, 'description'):
            meta_data['description'] = txt[:int(len(txt)/3)]

    # Download and cache the thumbnail
    if thumbnail_addr:
        thumbnail_img = soup.find('img', {"class": "ipc-image"})
        if thumbnail_img:
            icon_url = thumbnail_img['src']
            if icon_url:
                get_image(icon_url, thumbnail_addr)
        else:
            print("Can't find an image.")

    # Get the genres
    genres_box = soup.find("div", {"data-testid": "genres"})
    if genres_box:
        genre_list = [div.get_text() for div in genres_box.find_all("span")]

        meta_data["nsfw"] = False

        if fmt_check(genre_list, "tags"):
            meta_data["tags"] = genre_list

            if "Hentai" in genre_list or "Ecchi" in genre_list:
                meta_data["nsfw"] = True

    meta_data["visited_imdb"] = True

    return meta_data
