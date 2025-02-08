from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
import os

def music_extensions():
    return ["flac", "mp3", "m4a"]

def playlist_extensions():
    return ["xspf", "m3u", "m3u8"]

def audio_tags():
    return {
        "flac": {"function": FLAC, "title": "title", "artist": "artist"},
        "mp3":  {"function": MP3, "title": "TIT2", "artist": "TPE1"},
        "m4a":  {"function": MP4, "title": "©nam", "artist": "©ART"}
    }

# return a tuple for (file_name, extension_of_file)
def file_name_ext(filename):
    ext = filename.split('.')[-1]
    filename = filename.split('/')[-1].split('.' + ext)[0]
    return (filename, ext)

# walk all files in provided base directory
# manages buffer by saving returns in list for each iteration
def all_files_in(base_dir="new downloads/"):
    if not isinstance(base_dir, list):
        base_dir = [base_dir]

    file_paths = []
    for dir in base_dir:
        for root, _, files in os.walk(dir):
            for file in files:
                file_path = os.path.join(root, file).replace("\\", "/")
                file_paths.append(file_path)

    return file_paths


def make_list(param):
    if not isinstance(param, list):
        param = [param]
    return param
    

if __name__ == "__main__":
    print(file_name_ext("as/bas/has.txt"))