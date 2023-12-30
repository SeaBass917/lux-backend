# =======================================================
# Description: Fix duplicate descriptions in the database
# =======================================================
import pymongo


def main():

    db = pymongo.MongoClient("mongodb://localhost:27017/")
    db_metadata = db["mediaMetadata"]
    collection = db_metadata["video"]

    docs = collection.find({})

    for doc in docs:
        title = doc['_id']
        if "description" not in doc:
            print(f"Missing description in doc {title}")
            continue
        desc = doc["description"]

        len_third = int(len(desc)/3)
        if desc[:len_third] == desc[len_third:len_third*2]:
            collection.update_one(
                {"_id": title}, {"$set": {"description": desc[:len_third]}})

    return


if __name__ == "__main__":
    main()
