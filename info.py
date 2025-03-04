from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TCON
import os

def music_extensions():
    return ["flac", "mp3", "m4a"]

def playlist_extensions():
    return ["xspf", "m3u", "m3u8"]

# print all tags of audio file for analysis
def all_tags(filename):
    audio = File(filename)
    for tag, value in audio.tags.items():
        if len(str(value)) < 10000:
            print(tag, value, sep=": ")

def audio_tags():
    return {
        "flac": {"function": FLAC, "title": "title", "artist": "artist", "genre": "genre"},
        "mp3":  {"function": MP3, "title": "TIT2", "artist": "TPE1", "genre": "TCON"},
        "m4a":  {"function": MP4, "title": "©nam", "artist": "©ART", "genre": "©gen"}
    }

def save_audio(audio):
    audio.save()

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
    

def sorted_m3u(m3u):
    m3u = m3u.split("\n")
    new_m3u = []

    for i in range(2, len(m3u)-1, 2):
        print(m3u[i])
        name = m3u[i].split(',', 1)[1].lower()
        new_m3u.append((name, m3u[i], m3u[i+1]))

    new_m3u.sort()
    return "\n".join(m3u[:2] + [line for _, line1, line2 in new_m3u for line in [line1, line2]]) 

if __name__ == "__main__":
    print(file_name_ext("as/bas/has.txt"))