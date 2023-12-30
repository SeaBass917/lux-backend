# ============================================================ #
# Author:       S e a B a s s
# Create Date:  20 Feb 2022
# 
# Project:      Lux
# Filename:     convertVideosToMKV.py
# 
# Description:  Search the video media folders for any non-mkv 
#               video file.
#               If any are found:
#                   - Convert them to MKV
#                   - Move the original file to a recycle bin
#                   - Extract the subtitles into a local srt.
# 
# ============================================================ #
import os

SUPPORTED_VID_EXT = ".mkv"
SUPPORTED_SUB_EXT = ".srt"

# =========
# Checkers
# =========

def is_non_supported_type(filename : str):
    """Return true if the file is a type we need to convert.
    Currently that is anything not an MKV
    """
    return not filename.lower().endswith(SUPPORTED_VID_EXT)

def is_subtitle_extracted(root: str, filename: str):
    """Check if the subtitle has been extracted yet.
    It will be in the same folder with the same name, 
    but with the SUPPORTED_SUB_EXT
    
    Raises
    ------
    ValueError 
        If the file passed is not the expected video
        file extension.          
    """
    if filename.lower().endswith(SUPPORTED_VID_EXT):
        filename_sub = filename[:-len(SUPPORTED_VID_EXT)] + SUPPORTED_SUB_EXT
        return os.path.exists(os.path.join(root, filename_sub))
    else:
        raise ValueError(f"{filename} is not a supported video type. "
            f"Expected a(n) {SUPPORTED_VID_EXT}")

# ===========
# Converters
# ===========

def convert_mp4_to_mkv(root: str, filename: str, filename_new: str):
    """Convert an MP4 file to MKV format.
    Writes file to filename_new.

    Input
    -----
    root: str
        Directory of the input file, 
        and the directory for our output file.
    filename: str
        Name of the input file. (Extension included)
    filename_new: str
        Name for the output file. (Extension included)
    """
    raise NotImplementedError(f"No support yet for filetype: mp4")

def convert_avi_to_mkv(root: str, filename: str, filename_new: str):
    """Convert an AVI file to MKV format.
    Writes file to filename_new.

    Input
    -----
    root: str
        Directory of the input file, 
        and the directory for our output file.
    filename: str
        Name of the input file. (Extension included)
    filename_new: str
        Name for the output file. (Extension included)
    """
    raise NotImplementedError(f"No support yet for filetype: avi")

def converter_dispatch(root: str, filename: str):
    """Dispatch function for routing a given file 
    to it's converter method

    Returns
    -------
    filename_new : str
        New filename after the type conversion.
    """
    dispatch_map = {
        ".mp4": convert_mp4_to_mkv,
        ".avi": convert_avi_to_mkv,
    }

    ext_ignore = [".meta", ".srt"]

    # Get the new filename + current extension
    filename_noext, ext = os.path.splitext(filename)
    filename_new = filename_noext + SUPPORTED_VID_EXT
    ext = ext.lower()

    if ext in dispatch_map.keys():
        dispatch_map[ext](root, filename, filename_new)
    elif ext not in ext_ignore:
        path = os.path.join(root, filename)
        raise ValueError(f"Unexpected filetype in video folder: {path}")

    return filename_new

# ===================
# Subtile Extraction
# ===================

def sub_extracter(root: str, filename: str):
    """Extract the subtitles from an MKV file and subtitle extraction method
    """
    print()

# =================
# Main Entry Point
# =================
if __name__ == "__main__":
    
    DIR_VIDEOS = "videos/"
    
    for root, dirnames, filenames in os.walk(DIR_VIDEOS):
        for filename in filenames:

            try:
                # If we don't support this type convert it
                if is_non_supported_type(filename):
                    filename = converter_dispatch(root, filename)

                # Check if we have the subtitels extracted yet
                if is_subtitle_extracted(root, filename):
                    sub_extracter(root, filename)
            
            except NotImplementedError as e:
                print(e)
            except ValueError as e:
                print(e)

