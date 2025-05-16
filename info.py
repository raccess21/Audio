from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TCON, TALB
import os
from ytmusicapi import YTMusic
import json
import ast

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
        "flac": {"function": FLAC, "title": "title", "artist": "artists", "genre": "genre", "album": "album"},
        "mp3":  {"function": MP3, "title": "TIT2", "artists": "TPE1", "genre": "TCON", "album": "TALB"},
        "m4a":  {"function": MP4, "title": "©nam", "artists": "©ART", "genre": "©gen", "album": "©alb"},
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
        try:
            name = m3u[i].split(',', 1)[1].lower()
            new_m3u.append((name, m3u[i], m3u[i+1]))
        except Exception as e:
            print(e, m3u[i], sep="$$ ")
    new_m3u.sort()
    return "\n".join(m3u[:2] + [line for _, line1, line2 in new_m3u for line in [line1, line2]]) 

def clean_tag(ext, file_path):
    tags = audio_tags()[ext]
    audio = tags["function"](file_path)
    
    song = {
        "title" : str(audio[tags["title"]]),
        "artists" : str(audio[tags["artists"]]),
        "genre" : str(audio[tags["genre"]]),
        "album" : str(audio[tags["album"]]),
        "path": file_path.split("Audio/")[-1],
        "duration": round(audio.info.length),
    }
    
    # Helper to safely parse and clean list-like fields
    def clean_mp3(song):
        song["artists"] = [a.strip() for a in song["artists"].replace(',', ';').split(";")]
        song["genre"] = [a.strip() for a in song["genre"].replace("\u0000", ";").split(";")]
        return song
    
    def clean_m4a(song):
        song["title"] = ast.literal_eval(song["title"])[0]
        song["artists"] = ast.literal_eval(song["artists"])
        song["genre"] = ast.literal_eval(song["genre"].replace("; ", "', '"))
        song["album"] = song["album"].split("'")[1]
        return song

    def clean_flac(song):
        ...

    cleaners = {
        "flac": clean_flac,
        "mp3": clean_mp3,
        "m4a": clean_m4a    
    }
    song = cleaners[ext](song)
    title = song.pop("title")
    return title, song

def all_songs_dict(base_dir=["lossy/"]):
    try:
        with open("web_assets/songs.json", "r") as f:
            songs = json.loads(f.read())
    except FileNotFoundError:
        songs = {}
    
    for i, file_path in enumerate(all_files_in(base_dir=base_dir)):
        name, ext = file_name_ext(file_path)
        if ext in music_extensions() and file_path not in songs:
            print(i, name, ' ', sep='"')
            title, song = clean_tag(ext, file_path)
            songs[title] = song

    with open("web_assets/songs.json", "w") as f:
        f.write(json.dumps(songs, indent=4))

    # for file_path in all_files_in(base_dir=["lossy/"]):
    #     name, ext = file_name_ext(file_path)
    #     # if ext in music_extensions():
    #     if ext == "m4a":
    #         print(name)
    #         fname = file_path.split("." + ext)[0]
    #         os.rename(file_path, file_path.replace("lossy/", "new downloads/"))
    #         os.rename(f"{fname}.lrc", f"{fname}.lrc".replace("lossy/", "new downloads/"))

# search algo to match youtube songs with local songs
def get_playlist(id="PLlXEnX_5coLUM5Sn_YV1ldufT55OxP9VS"):
    with open("web_assets/songs.json", "r") as f:
        songs = json.loads(f.read())
    
    yt = YTMusic()
    playlist = yt.get_playlist(id)
    
    print(playlist["title"])

    # title: Start A Fire: 
    # artists: [{'name': 'John Legend', 'id': 'UC7wYAi5loaBGEbOQz7VBF2w'}]
    found = 0
    for track in playlist["tracks"]:
        if track["title"] in songs:
            found += 1
            print(found, track["title"], sep=". ")


if __name__ == "__main__":
    # with open("web_assets/yt_playlists.json", "r") as f:
    #     playlists = json.loads(f.read())
    
    # for playlist in playlists:
    #     get_playlist(playlists[playlist])
    #     print("\n\n")
    all_songs_dict()