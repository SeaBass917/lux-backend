# Wiki

## (MongoDB)

### Docker Run Command

Prod Environment

```bash
s docker run \
    -p 27017:27017 \
    --name media-nosql-db \
    -v ~/mongo/media-db:/var/lib/mongodb \
    -v ~/mongo/mongod.conf:/etc/mongod.conf \
    -v /etc/timezone:/etc/timezone:ro \
    -v /etc/localtime:/etc/localtime:ro \
    -d mongo
```

Dev environment

```bash
s docker run \
    -p 27018:27017 \
    --name media-nosql-db-dev \
    -v ~/mongo/media-db-dev:/var/lib/mongodb \
    -v ~/mongo/mongod.conf:/etc/mongod.conf \
    -v /etc/timezone:/etc/timezone:ro \
    -v /etc/localtime:/etc/localtime:ro \
    -d mongo
```

### Docker Clear logs

```sh
sudo sh -c 'echo "" > $(docker inspect --format="{{.LogPath}}" my-app)'
```

### Backup DB

COMMAND PID TID TASKCMD USER FD TYPE DEVICE SIZE/OFF NODE NAME

```sh
mongodump -o ~/db-backups/media-db/
mongodump -o ~/seastorage-V/db-backups/media-db/
```

### Restore DB

```sh
mongorestore ~/db-backups/media-db/
```

or if you want to match the backup exactly (dropping all active docs)
This is usually what you want in a restore on this project

```sh
mongorestore --drop ~/db-backups/media-db/
```

## API

### GET Media Requests

```
/GetMusicArtistIndex
    On Success: 200
    Returns an index of Music Artists under the following schema:
    [
        {
            title : "Title String",
            icon_addr : "images/lux/thumbnails/music/${title}.jpg",
        },
        ...
    ]
    Failure 500
    The server index is flagged as not good.

/GetMangaIndex
    On Success: 200
    Returns an index of Manga Selections under the following schema:
    [
        {
            title : "Title String",
            nsfw : true/false,
            author : doc["author"],
            icon_addr : "images/lux/thumbnails/manga/${title}.jpg",
        },
        ...
    ]
    Failure 500
    The server index is flagged as not good.

/GetVideoIndex
    On Success: 200
    Returns an index of Video Selections under the following schema:
    [
        {
            title : "Title String",
            nsfw : true/false,
            icon_addr : "images/lux/thumbnails/video/${title}.jpg",
        },
        ...
    ]
    Failure 500
    The server index is flagged as not good.

/GetMangaMetaDataByTitle
    On Success: Returns a 207.
    The data will be contained in a list with the following schema:
        {
            data: {...metadata...},
            status: 200|404,
            message: "String" (Only used when a 404),
        }
    Failure 500
    Caused by Database errors
    Failure 400
    Issue in the request string.
    Failure 404
    Sent if there is no valid data to return.
    e.g. ALL requested items were not found in the DB.

/GetVideoMetaDataByTitle
    On Success: Returns a 207.
    The data will be contained in a list with the following schema:
        {
            data: {...metadata...},
            status: 200|404,
            message: "String" (Only used when a 404),
        }
    Failure 500
    Caused by Database errors
    Failure 400
    Issue in the request string.
    Failure 404
    Sent if there is no valid data to return.
    e.g. ALL requested items were not found in the DB.

/GetMangaChaptersByTitle
    On Success: Returns a 207.
    The data will be contained in a list with the following schema:
        {
            data: {
                chapters: {
                    ch1: ["pg1.jpg", "pg2.jpg", ...],
                    ... },
                titlePath: "path/to/title",
            },
            status: 200|404,
            message: "String" (Only used when a 404),
        }
    Failure 500
    Caused by Database errors
    Failure 400
    Issue in the request string.
    Failure 404
    Sent if there is no valid data to return.
    e.g. ALL requested items were not found in the DB.

/GetVideoEpisodesByTitle
    On Success: Returns a 207.
    The data will be contained in a list with the following schema:
        {
            data: {
                episodes: ["episode1.mkv", "episode2.mkv", ...],
                titlePath: "path/to/title",
            },
            status: 200|404,
            message: "String" (Only used when a 404),
        }
    Failure 500
    Caused by Database errors
    Failure 400
    Issue in the request string.
    Failure 404
    Sent if there is no valid data to return.
    e.g. ALL requested items were not found in the DB.

/GetSubtitleSelectionsForEpisode
    On success 200 | 204
    200 - ["English 1", "English 2", "Espanol 1", ...]
    204 - No results found for title.
    Failure 500
    Request is valid, but data is bad.
    Failure 400
    Issue in the request string.

/GetSubtitlesChewieFmt
    On success 200
    200 - [{index: 0, start_ms: 0, end_ms: 10, text: "..."}, ...]
    Failure 500
    Request is valid, but data is bad.
    Failure 400
    Issue in the request string.
    Failure 404
    Client requested something we don't have.
    e.g. bad title, episode, or track string.
```
