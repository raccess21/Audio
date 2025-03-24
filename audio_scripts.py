import os
from lxml import etree
import subprocess
import sys
from lyrics_scripts import all_files_in, save_all_lyrics_for_web_assets
import info

folders = ["files"] 

def rename_file_git(file_counter, file_path):
    # skip_extensions = [".xspf", ".m3u", ".json"]
    
    """
    Recursively rename files in a directory by replacing spaces with underscores.
    Use `git mv` to stage the renames in Git.
    """
    new_path = "new path"

    # Rename the file if it contains spaces
    if file_path != new_path:
        try:
            # Stage the rename in Git
            subprocess.run(["git", "mv", file_path, new_path], check=True)
            print(f"{file_counter}. Renamed and staged: {file_path} -> {new_path}")
            return (1, None)
        except subprocess.CalledProcessError as e:
            print(f"Error staging {file_path} -> {new_path} in Git: {e}")
    return (0, None)

def remove_tags(root, tags, ns):
    if not isinstance(tags, list):
        tags = [tags]
    
    for tag in tags:
        # Find all instances of the tag using XPath with namespace
        elements = root.xpath(f".//default:{tag}", namespaces=ns)
        for element in elements:
            # Remove each found element
            element.getparent().remove(element)

    

def xml_clean_vlc(root, ns):
    # remove unnecessary tags from track data
    bad_tags = ["image", "annotation", "extension"]    
    remove_tags(root, bad_tags, ns)

    # File location edit for local files relative paths
    for location_tag in root.xpath("//default:location", namespaces=ns):
        location_tag.text = location_tag.text.replace("file:///C:/rahul/Audio/", "../")


from lxml import etree

def xspf_to_m3u(root, ns, playlist_name="Playlist", web=True):
    m3u = f"#EXTM3U\n#PLAYLIST:{playlist_name}\n"
    
    # Iterate through <track> elements
    for track in root.xpath("//default:track", namespaces=ns):
        location = track.find("default:location", namespaces=ns)
        if web:
            if "lossy" not in location.text:
                continue

        # title = location for web stream to lrc resoltion for poweramp
        title, _ = info.file_name_ext(location.text.split('/')[-1])
        title = title.replace('%20', ' ')
        duration = track.find("default:duration", namespaces=ns)

        if location is not None:
            # Write the extended info line if available
            duration_ms = int(duration.text) if duration is not None else -1
            m3u += f"#EXTINF:{duration_ms // 1000},{title}\n"

            # Write the file location
            m3u += f"{location.text}\n"
    return m3u


# local and web playlist in m3u for musicbee/musicolet don't support xspf
def playlists_from_xspf(file_name = "all.xspf", playlist_title = "Playlist"):
    # Define namespaces
    ns = {
        'default': "http://xspf.org/ns/0/",
    }
    
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(f"playlists temp/{file_name}", parser)
    root = tree.getroot()
    
    title_tag = root.xpath("//default:title", namespaces=ns)[0]
    
    if root.xpath("//default:extension", namespaces=ns):
        xml_clean_vlc(root, ns)

    # File location edit for server files 
    # plylist export absolute path will always contain Audio -> reform into relative path
    for location_tag in root.xpath("//default:location", namespaces=ns):
        location_tag.text = "../" + location_tag.text.split("Audio/")[1]
            
    #writing m3u local files
    with open(f"playlists/{info.file_name_ext(file_name)[0]}.m3u", 'w') as fo:
        fo.write(xspf_to_m3u(root, ns, playlist_title))
        print(f"{file_name} Local m3u Cleaned and written")

    # File location edit for server files 
    for location_tag in root.xpath("//default:location", namespaces=ns):
        location_tag.text = "https://raw.githubusercontent.com/raccess21/Audio/main/" + location_tag.text.split("../")[1]
        
    #writing m3u local files
    with open(f"playlists web/{file_name.split('.')[0]} web.m3u", 'w') as fo:
        fo.write(xspf_to_m3u(root, ns, playlist_title))
        print(f"{file_name} Local m3u Cleaned and written")


def playlists_from_m3u(file_name, playlist_title = "Playlist"):
    with open(f"playlists temp/{file_name}", 'r') as f:
        m3u = f.readlines()

    # file location edit for relative path local files
    for i in range(2, len(m3u), 2):
        m3u[i] = "../" + m3u[i].split("Audio/")[1]

    # track info embed
    if "#EXTINF:" not in m3u[1]:
        for i in range(1, len(m3u), 2):
            name, artists = m3u[i+1].replace("_", " ").split("/")[-1].split(".")[0].split('-')
            m3u[i] = f"#EXTINF:100,{name} - {artists}\n"
            # track duration code pending
    
    # add playlist name tag if not present
    if "#PLAYLIST:" not in m3u[1]:
        m3u.insert(1, f"#PLAYLIST:{playlist_title}\n")

    m3u = "".join(m3u)

    # write local file m3u playlist
    with open(f"playlists/{file_name.split('.')[0]}.m3u", 'w') as fo:
        fo.write(m3u)

    # write web m3u playlist
    with open(f"playlists web/{file_name.split('.')[0]} web.m3u", 'w') as fo:
        fo.write(m3u.replace("../", "https://raw.githubusercontent.com/raccess21/Audio/main/"))


def m3u_web_string_for_file(file_counter, file_path):
    file_name, ext = info.file_name_ext(file_path)
    print(f"{file_counter}. {file_path} done.")
    audio = info.audio_tags()[ext]["function"](file_path)
    duration = round(audio.info.length)
    
    value = f"\n#EXTINF:{duration},{file_name}\n"
    full_path = os.path.abspath(file_path).replace("\\", "/")

    # ' ' replaced by %20 to make stream work on poweramp
    value += f"https://raw.githubusercontent.com/raccess21/Audio/main/{full_path.split('Audio/')[1].replace(' ', '%20')}"
    return value

# return valid m3u by removing non existent songs from the list
def checked_playlist(fi):
    playlist = fi.readlines()
    new_playlist = playlist[:2]
    
    for i in range(2, len(playlist), 2):
        song_path = playlist[i+1].split("main/")[1].replace("%20", " ").strip('\n')
        if os.path.exists(song_path):
            new_playlist += [playlist[i], playlist[i+1]]

    return "".join(new_playlist)


# save all lyrics for web assets and create web playlist
def default_all_web():
    try:
        with open("playlists web/All Web.m3u", "r", encoding='UTF-8') as fi:
            data = checked_playlist(fi)
    except FileNotFoundError:
        data = "#EXTM3U\n#PLAYLIST:All Songs\n"

    
    file_counter = 0
    music_extensions = info.music_extensions()

    for file_path in info.all_files_in(base_dir=["lossy/", "lossy_web"]):
        file_name, ext = info.file_name_ext(file_path)
        if ext in music_extensions:
            if file_path.replace(" ", "%20") not in data:
                file_counter += 1
                data += m3u_web_string_for_file(file_counter, file_path)
    
    
    with open("playlists web/All Web.m3u", "w", encoding='UTF-8') as fo:
        fo.write(info.sorted_m3u(data))
        print("Updated: All Web.m3u")
    
    # all_files_in(["lossy/", "lossless/"] save lrc for web assets)
    save_all_lyrics_for_web_assets()
    
    # save all songs metadata as json
    info.all_songs_dict()


def main():
    # for file_name in os.listdir("playlists temp"):
    #     if file_name.split(".")[1] in info.playlist_extensions():
    #         playlist_title = file_name.split('.xspf')[0].strip()
    #         playlists_from_xspf(file_name, playlist_title)
    # playlists_from_xspf("All Songs.xspf", "All Songs")
    # rename_files_recursively("lossy/")
    # playlists_from_m3u("Musicolet.m3u")
    default_all_web()
    



if __name__ == "__main__":
    main()