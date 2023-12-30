# Read in media from the download folders and organize them in the filesystem for 
# File orginization is designed to simplify human navigation
# 
# Movies
#   | ({Date}) {Title}
#     | {Title}.mkv
# Shows
#   | {Series Title A}
#     | Season {N}
#       | {Series Title A} - S{N} E{K}.mkv
# Music
#   | {Artist}
#     | ({Date}) {Album} [{FMT}]
#       | {Song Title}.{FMT}
# Manga
#   | {Title}
#     | {Volume|Chapter}
#       | {Title} Page {N}.{jpg|png}
# Images
#   | {Folder}
#     | {Name}.{jpg|png}

from dataclasses import dataclass
from enum import Enum
import os
import subprocess


DOWNLOADS_FOLDER = "./media-dls/"
MANGA_DLS_FOLDER = DOWNLOADS_FOLDER+"manga/"
MUSIC_DLS_FOLDER = DOWNLOADS_FOLDER+"music/"
VIDEO_DLS_FOLDER = DOWNLOADS_FOLDER+"videos/"
IMAGE_DLS_FOLDER = DOWNLOADS_FOLDER+"images/"

MEDIA_FOLDER = "./"
MANGA_FOLDER = MEDIA_FOLDER+"manga/"
MUSIC_FOLDER = MEDIA_FOLDER+"music/"
VIDEO_FOLDER = MEDIA_FOLDER+"videos/"
IMAGE_FOLDER = MEDIA_FOLDER+"images/"

class FFProbeParseer():
    """Utility class used to extract metadata from a
    data dump from ffprobe."""

class Encoding(Enum):
    UNK = 0
    MP3 = 1
    FLAC = 2
    WAV = 3
    MKV = 4
    MP4 = 5

    @staticmethod
    def to_string(n):
        if n == Encoding.MP3:
            return ".mp3"
        elif n == Encoding.FLAC:
            return ".flac"
        elif n == Encoding.WAV:
            return ".wav"
        elif n == Encoding.MKV:
            return ".mkv"
        elif n == Encoding.MP4:
            return ".mp4"
        else:
            return "<unk>"

    @staticmethod
    def from_string(s : str):
        if s == ".mp3":
            return Encoding.MP3
        elif s == ".flac":
            return Encoding.FLAC
        elif s == ".wav":
            return Encoding.WAV
        elif s == ".mkv":
            return Encoding.MKV
        elif s == ".mp4":
            return Encoding.MP4
        else:
            return Encoding.UNK

@dataclass
class MusicMetaData():
    title : str
    album : str
    artist : str
    date : str
    encoding : Encoding
    # title           : As The Sky Lay Burning
    # copyright       : 2008 Angel Vivaldi
    # album           : Revelations
    # track           : 1/8
    # album_artist    : Angel Vivaldi
    # disc            : 1/1
    # artist          : Angel Vivaldi
    # genre           : Neo-Classical Djent
    # date            : 2008

    # TITLE           : Face of Death
    # Album           : Dreamless
    # Artist          : Fallujah
    # Genre           : Death Metal
    # COUNTRY         : United States
    # ORGANIZATION    : Nuclear Blast
    # CATALOG         : NE3709-2
    # ENCODER         : FLAC 1.2.1
    # disc            : 1
    # TOTALDISCS      : 1
    # TOTALTRACKS     : 12
    # DATE            : 2016
    # track           : 1

def get_metadata_raw(path : str):
    """Returns the unfiltered metadata for a 
    provided file.

    Inputs
    ------
    path : str
        Path to the file requested.1

    Return
    ------
    metdata : dict
        Dictionary of key-value pairs for each 
        piece of metadata extracted from the file.
    """
    _, ext = os.path.splitext(path)
    ext = ext.lower()

    # Metadata from the file
    metadata = {}
    if ext in [".mp3", ".flac", ".mkv"]:

        # Use FFMPEG to get the metadata from this file
        output = subprocess.run(
            ["ffmpeg", "-i", path], capture_output=True)

        stdout = str(output.stderr).replace("\\n", "\n")

        # Isolate the part of the string that is just meta data
        i_beg = stdout.find("Metadata:")
        i_end = stdout.find("Duration:", i_beg)
        metadata_substr = stdout[i_beg+len("Metadata:"):i_end]
        metadata_substr = metadata_substr.strip()

        # For each line in the metadata, extract the data
        # Should look like the following:
        #   album   : abc
        #   artist  : 123
        for line in metadata_substr.split("\n"):
            pair = line.strip().split(":")

            if 2 <= len(pair):
                key = pair[0].strip().lower()
                val = (":".join(pair[1:])).strip()
                metadata[key] = val

        return metadata
    else:
        raise RuntimeWarning(f"File \"{path}\" is not a known media file.")

def prune_empty_dirs(path : str):
    """Removes all empty directories from a given path."""
    for root, _, files in os.walk(path, topdown=False):
        if root != path and 0 == len(files):
            os.rmdir(root)

def process_dls(dl_folder : str):
    for root, _, files in os.walk(dl_folder):
        for file in files:
            file_path = root + "/" + file
            _, ext = os.path.splitext(file)

            metadata_raw = get_metadata_raw(file_path)

            metadata = MusicMetaData(
                title    =  metadata_raw["title"], 
                album    =  metadata_raw["album"],
                artist   =  metadata_raw["artist"],
                date     =  metadata_raw["date"],
                encoding =  Encoding.from_string(ext),
                )

def main():
    process_dls(MUSIC_DLS_FOLDER)

if __name__ == "__main__":
    main()