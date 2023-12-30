# ============================================================================ #
# This script's purpose was to leverage the window FS "Date modified" to
# initialize the dateAdded fields to the DB
# ============================================================================ #
import datetime
import os
import pymongo


manga_folder = "manga/"
video_folder = "videos/"


def add_dateAdded(media_folder: str, collection: pymongo.MongoClient):
    for title in os.listdir(media_folder):
        title_dir_path = f"{media_folder}{title}"
        dateAdded = datetime.datetime.fromtimestamp(
            os.path.getmtime(title_dir_path))

        collection.update_one(
            {"_id": title}, {"$set": {"dateAdded": dateAdded}})


def main():
    db = pymongo.MongoClient("mongodb://localhost:27017/")
    db_metadata = db["mediaMetadata"]

    add_dateAdded(manga_folder, db_metadata["manga"])
    add_dateAdded(video_folder, db_metadata["video"])

    db.close()


if __name__ == "__main__":
    main()
