class VideoMetaData {
  constructor(metaDataObj) {
    const dateAdded = metaDataObj["dateAdded"];

    this.title = metaDataObj["title"];
    this.nsfw = metaDataObj["nsfw"];
    this.studio = metaDataObj["studio"];
    this.staff = metaDataObj["staff"];
    this.yearStart = metaDataObj["yearstart"];
    this.yearEnd = metaDataObj["yearend"];
    this.producer = metaDataObj["producer"];
    this.englishLicense = metaDataObj["english_license"];
    this.visitedMal = metaDataObj["visited_mal"];
    this.director = metaDataObj["director"];
    this.tags = metaDataObj["tags"];
    this.visitedIMDB = metaDataObj["visited_imdb"];
    this.visitedWikipedia = metaDataObj["visited_wikipedia"];
    this.dateAdded = dateAdded ? new Date(dateAdded) : null;
    this.description = metaDataObj["description"];
  }

  /**
   * Checks if the required fields for a thumbnail are present.
   * @returns {bool}  True if all required fields are present.
   */
  checkRequiredFieldsThumbnail() {
    return this.title != null && this.nsfw != null;
  }

  /**
   * Checks if the required fields for an info page are present.
   * @returns {bool}  True if all required fields are present.
   */
  checkRequiredFieldsInfoPage() {
    return (
      this.title != null &&
      this.description != null &&
      this.tags != null &&
      this.yearStart != null
    );
  }
}

export default VideoMetaData;
