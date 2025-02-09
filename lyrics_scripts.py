import syncedlyrics
import os
import re
from mutagen import File
from mutagen.id3 import ID3, USLT, SYLT, Encoding
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
import chardet
from shutil import copyfile
import pyperclip
import info 

# extensions supported

#music_extensions = ['.flac', '.mp3', ".m4a"]
music_extensions = ['flac', 'mp3', "m4a"]
def search_lyrics(song_name, duration=0):
    lyrics = syncedlyrics.search(song_name)
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

# saves lyrics to file 
# return 1 if successfully fetches and save lyrics else return 0
def save_lyrics(dirs=["new downloads/"]):
    file_counter = 0
    dirs = info.make_list(dirs)
    for file_path in info.all_files_in(dirs):
        filename, ext = info.file_name_ext(file_path)
        
        if ext in music_extensions:
            filename = file_path.split("." + ext)[0] + ".lrc"        
            # if lrc file does not exist search and write lyrics
            if not os.path.exists(filename):
                file_counter += 1
                lyrics = get_lyrics(file_path)
                if lyrics:
                    write_lrc(filename, lyrics)
                    print(f"{file_counter}. {filename} written")
                else:
                    write_lrc(filename, "Not Found")

# walk all files in provided base directory
# manages buffer by saving returns in list for each iteration
def all_files_in(base_dir="new downloads/", next_function=save_lyrics, buffer=[None]):
    base_dir = info.make_list(base_dir)

    file_counter = 1                                                       #file counter
    for dir in base_dir:
        for root, _, files in os.walk(dir):
            for file in files:
                file_path = os.path.join(root, file).replace("\\", "/")
                res = next_function(file_counter, file_path)
                file_counter += res[0]
                if res[1]:
                    buffer.append(res[1])

    return buffer

# save all lrc files in in web_assets 
def save_all_lyrics_for_web_assets(dirs=["lossy/", "lossless/"]):
    if not os.path.exists("web_assets/lyrics/"):
        os.mkdir("web_assets/lyrics/")

    filecounter = 1
    for file_path in info.all_files_in(dirs):
        file_name = file_path.split("/")[-1]
        if ".lrc" in file_name and file_name not in os.listdir("web_assets/lyrics/"):
            copyfile(file_path, f"web_assets/lyrics/{file_name}")
            print(f"{filecounter}. {file_name} written to web assets.")
            filecounter += 1



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
    
    # get_lyrics("You_Belong_With_Me_-_Taylor_Swift.m4a")
    # save_all_lyrics_for_web_assets()
    # all_tags("lossy/Co2.mp3")
    # pyperclip.copy(search_lyrics("November Rain"))
    
    # download lyrics for new new downloads
    save_lyrics()

    