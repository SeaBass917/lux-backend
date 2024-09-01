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
# Description:  Refresh/populate the server subtitles data.
#               Flutter currently won't support subtitles streaming, so the
#               subtitles need to be managed separately.
#               This will be done through the database.
#               If this can be fixed on the Flutter side,
#               please depricate this.
#
# ============================================================================ #

import os
import re
import pymkv
import subprocess
import pymongo
import configparser
# import ass
# import pysrt


def clean_ass_text(text: str) -> str:
    return re.sub("{[^}]+}", "", text.replace("\\N", "\n"))


def subtrack_to_key(subtrack: dict) -> str:
    def clean(s: str) -> str: return s.replace('.', '').replace('/', '')
    return clean(subtrack.track_name) if subtrack.track_name else f"{clean(subtrack.language)}-{subtrack.track_id}"


def get_subtitle_tracks_mkv(path_episode: str) -> list:
    try:
        mkv = pymkv.MKVFile(path_episode)
        subtitle_tracks = [(subtrack_to_key(track), track)
                           for track in mkv.tracks if track.track_type == 'subtitles']
        return subtitle_tracks
    except BaseException as e:
        print(e)

    return []


def extract_subtitles_mkv(path_episode: str, subtitles_out_dir: str,  track: pymkv.MKVTrack) -> bool:

    ext = ""
    if track.track_codec == "SubStationAlpha":
        ext = "ass"
    elif track.track_codec == "SubRip/SRT":
        ext = "srt"
    elif track.track_codec == "VobSub":
        ext = "vob"
        print("  TODO: Implement VobSub OCR conversion...")
        return False
    else:
        # raise Exception(f"Help idk what to do with \"{track.track_codec}\"")
        print(f"   Help idk what to do with \"{track.track_codec}\"")
        return False

    # Path to subtitles will follow an identicle structure as the video path
    filename = os.path.splitext(os.path.basename(path_episode))[0]
    path_subtitles_out = f"{subtitles_out_dir}/{filename}.{subtrack_to_key(track)}.{ext}"

    try:
        # Extract the subtritles into an srt file
        status_extract = subprocess.run(["mkvextract",
                                        path_episode,
                                        "tracks",
                                         f"{track.track_id}:{path_subtitles_out}"],
                                        check=True)
        if status_extract.returncode != 0:
            print(
                f"Failed to extract subtitles track {track.track_id} from {path_episode}")
            return False

    except subprocess.CalledProcessError as e:
        print(e)
        return False

    return True


def update_subtitle_db(path_videos: str, connection_str: str, overwrite=False):
    """Scan through all videos in the video folder and store their subtitles
    In the DB.
    By default, 
    Subtitles will not overwrite old subtitle data, and are stored as follows:

    ```
    Collection: `subtitles`
    "Series 1": {
        "episodes": {
            "ep1": {
                "lang1": [
                    {index: 0, start_ms: 0, end_ms: 10, text: "..."},
                    {index: 1, start_ms: 10, end_ms: 15, text: "..."},
                    {index: 2, start_ms: 17, end_ms: 20, text: "..."},
                    ...
                ],
                "lang2": [ ... ],
            },
            "ep2": { ... },
            "ep3": { ... },
            ...
        }
    }
    "Series 2": {
        "episodes": {...}
    }
    ```
    """

    # Grab a connection to the db

    # Grab the db
    db = pymongo.MongoClient(connection_str)
    db_metadata = db["mediaMetadata"]
    collection = db_metadata["subtitles"]

    # Loop through all episodes in the video collection
    for title in os.listdir(path_videos):
        path_title = f"{path_videos}/{title}"
        print(f"Processing {path_title}")
        for episode in os.listdir(path_title):
            path_episode = f"{path_title}/{episode}"
            filename, ext = os.path.splitext(episode)

            # Set up the output directory for
            subtitles_out_dir = f"./subtitles/{title}"
            if not os.path.exists(subtitles_out_dir):
                os.makedirs(subtitles_out_dir)

            # This only works on MKVs
            # And idk if I plan to support other formats tbh..
            if ext.lower() != ".mkv":
                continue

            # Extraction is VERY expensive
            # Before extracting anything,
            # first check to see if there is anything in this MKV
            # we don't already have in the db
            track_list = get_subtitle_tracks_mkv(path_episode)
            if not track_list:
                continue

            # This line is chaotic and beatuiful so we're keeping it
            # Essentially: Loop through all files in the directory that match the pattern of this episode
            # Extract the track_key from each file name and compare it to the track_keys in the mkv
            # If all are a match, then there is nothing to do here.
            subtitle_files = os.listdir(subtitles_out_dir)
            is_subtitles_on_file = subtitle_files and all(
                [f[len(filename)+1:-4] in [key for key, _ in track_list]
                 for f in subtitle_files if re.match(filename, f)])
            if is_subtitles_on_file:
                continue

            # Get the subtitles from each track
            for _, track in track_list:
                extract_subtitles_mkv(path_episode, subtitles_out_dir, track)


if __name__ == "__main__":
    if "DB_ADDRESS" not in os.environ:
        print("DB_ADDRESS was not set; required for this script.")
        exit(1)

    update_subtitle_db("./videos", os.getenv('DB_ADDRESS'))
