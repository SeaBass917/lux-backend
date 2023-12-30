# ============================================================================ #
# This script's purpose was to migrate the data from the old flat file 
# design, into mongodb.
# ============================================================================ #
import os
import configparser
import pymongo


manga_folder = "manga/"
video_folder = "videos/"
# image_folder = "~/seastorage-V/images/"
# music_folder = "~/seastorage-V/music/"

def as_bool(s):
    return True if s == "True" else False

def db_get_manga(title : str):
    pass

def migrate_manga(cparser : configparser.ConfigParser, collection : pymongo.MongoClient):
    for title in os.listdir(manga_folder):
        metadata_filepath = f"{manga_folder}{title}/info.meta"

        # Skip this migration if there is no data for this media, or
        # data has already been migrated
        if not os.path.exists(metadata_filepath): continue
        test = collection.find_one({"_id": title})
        if test: continue
        

        cparser.read(metadata_filepath)
        metadata = {key : val if val not in ["True", "False"] else as_bool(val) for key, val in cparser["DEFAULT"].items()}
        metadata["_id"] = title
        metadata["tags"] = metadata["tags"].split(", ")
        if "iconaddr" in metadata: metadata.pop("iconaddr")
        if "iconAddr" in metadata: metadata.pop("iconAddr")

        print(f"Inserting \"{title}\"...")

        collection.insert_one(metadata)
            
def migrate_videos(cparser : configparser.ConfigParser, collection : pymongo.MongoClient):
    for title in os.listdir(video_folder):
        metadata_filepath = f"{video_folder}{title}/info.meta"

        # Skip this migration if there is no data for this media, or
        # data has already been migrated
        if not os.path.exists(metadata_filepath): continue
        test = collection.find_one({"_id": title})
        if test: continue
        
        # NOTE videos "use"(still had) an old format
        with open(metadata_filepath) as fp_in:
            cparser.read_string("[DEFAULT]\n" + fp_in.read())

        metadata = {key : val if val not in ["True", "False"] else as_bool(val) for key, val in cparser["DEFAULT"].items()}
        metadata["_id"] = title
        metadata["title"] = title
        metadata["tags"] = metadata["tags"].split(", ")
        if "iconaddr" in metadata: metadata.pop("iconaddr")
        if "iconAddr" in metadata: metadata.pop("iconAddr")

        print(f"Inserting \"{title}\"...")

        collection.insert_one(metadata)


def main():
    cparser = configparser.ConfigParser()
    db = pymongo.MongoClient("mongodb://localhost:27017/")
    db_metadata = db["mediaMetadata"]

    migrate_manga(cparser, db_metadata["manga"])
    migrate_videos(cparser, db_metadata["video"])

if __name__ == "__main__":
    main()