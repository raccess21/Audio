import syncedlyrics
import os
import re
from mutagen import File
from mutagen.id3 import ID3, USLT, SYLT, Encoding
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
import chardet

# extensions supported

music_extensions = ['.flac', '.mp3', ".m4a"]

def search_lyrics(song_name, duration=0):
    lyrics = syncedlyrics.search(song_name)
    # pyperclip.copy(lyrics)
    return lyrics

def get_lyrics(file):
    # tag list for file types
    tags = {
        "flac": {"function": FLAC, "title": "title", "artist": "artist"},
        "mp3":  {"function": MP3, "title": "TIT2", "artist": "TPE1"},
        "m4a":  {"function": File, "title": "©nam", "artist": "©ART"}
    }
    # pending audio tags, vorbis, wav, opus, ogg

    ext = file.split('.')[-1].lower()
    tags = tags[ext]
    audio = tags["function"](file)
    
    # catch tag/corruption error
    try:
        if audio.tags is not None:
            # catch not found/timeout error
            try:
                lyrics = search_lyrics(str(audio[tags["title"]]) + " " + str(audio[tags["artist"]]))
                return lyrics
            except Exception as e:
                print(f"{e} : {file}")
                return False
    except Exception as e:
        print(f"{e} : {file}")
        return False  
    
# detect lyrics encoding and write as lrc file
def write_lrc(filename, lyrics = ""):
    use_encoding = chardet.detect(lyrics.encode())["encoding"]
    with open(filename, "w", encoding=use_encoding) as f:
        f.write(str(lyrics))

# regex pattern substitution for extension 
def remove_extension(filename, pattern=None):
    pattern = pattern or "|".join(re.escape(ext) for ext in music_extensions)
    return re.sub(pattern, "", filename)

# walk all files in provided base directory
def all_files_in(base_dir="./"):
    # pattern for extension removal
    pattern = "|".join(re.escape(ext) for ext in music_extensions)

    file_counter = 0                                                       #file counter
    for root, _, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file).replace("\\", "/")
            if os.path.splitext(file)[1].lower() in music_extensions:
                filename = remove_extension(file_path, pattern) + ".lrc"
                
                # if lrc file does not exist search and write lyrics
                if not os.path.exists(filename):
                    lyrics = get_lyrics(file_path)
                    if lyrics:
                        write_lrc(filename, lyrics)
                        file_counter += 1
                        print(f"{file_counter}. {filename} written")
                    else:
                        write_lrc(filename, "Not Found")

def clean_spam_tags():
    # web download tag remove
    # lyricist tag update
    
    ...
# print all tags of audio file for analysis
def all_tags(filename):
    audio = File(filename)
    for tag, value in audio.tags.items():
        if len(str(value)) < 10000:
            print(tag, value, sep=": ")

if __name__ == "__main__":
    os.system('cls')
    
    test_files = [
        "Brain Damage.mp3",
        "Vera.flac"
    ]

    # get_lyrics("You_Belong_With_Me_-_Taylor_Swift.m4a")
    all_files_in("lossless/Indian Ocean - Black Friday [2004-FLAC] {Times Music - TDIFI 027V}")
    # all_tags("lossy/Co2.mp3")