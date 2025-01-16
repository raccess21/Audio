import os
from lxml import etree
import subprocess

folders = ["files"] 
playlist_extensions = ["xspf", "m3u", "m3u8"]


def rename_files_recursively(base_dir):
    skip_extensions = [".xspf", ".m3u", ".json"]
    
    """
    Recursively rename files in a directory by replacing spaces with underscores.
    Use `git mv` to stage the renames in Git.
    """
    for root, _, files in os.walk(base_dir):
        for file in files:
            old_path = os.path.join(root, file)
            new_filename = file.replace(" ", "_")
            new_path = os.path.join(root, new_filename)

            if any(file.endswith(ext) for ext in skip_extensions):
                continue

            # Rename the file if it contains spaces
            if old_path != new_path:
                try:
                    # Stage the rename in Git
                    subprocess.run(["git", "mv", old_path, new_path], check=True)
                    print(f"Renamed and staged: {old_path} -> {new_path}")
                except subprocess.CalledProcessError as e:
                    print(f"Error staging {old_path} -> {new_path} in Git: {e}")


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

def xspf_to_m3u(root, ns, playlist_name="Playlist"):
    m3u = f"#EXTM3U\n#PLAYLIST:{playlist_name}\n"
    
    # Iterate through <track> elements
    for track in root.xpath("//default:track", namespaces=ns):
        location = track.find("default:location", namespaces=ns)
        title = track.find("default:title", namespaces=ns)
        duration = track.find("default:duration", namespaces=ns)

        if location is not None:
            # Write the extended info line if available
            if title is not None or duration is not None:
                duration_ms = int(duration.text) if duration is not None else -1
                m3u += f"#EXTINF:{duration_ms // 1000},{title.text if title is not None else 'Unknown'}\n"

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
    with open(f"playlists/{file_name.split('.')[0]}.m3u", 'w') as fo:
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
            name, artist = m3u[i+1].replace("_", " ").split("/")[-1].split(".")[0].split('-')
            m3u[i] = f"#EXTINF:100,{name} - {artist}\n"
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

def main():
    # for file_name in os.listdir("playlists temp"):
    #     if file_name.split(".")[1] in playlist_extensions:
    #         playlist_title = file_name.split('.xspf')[0].strip()
    #         playlists_from_xspf(file_name, playlist_title)
    playlists_from_xspf("Rockstar.xspf", "Rockstar")
    # playlists_from_m3u("Musicolet.m3u")
if __name__ == "__main__":
    main()