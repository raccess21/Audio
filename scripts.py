import os
import json
from lxml import etree
import eyed3

folders = ["files"] 


# clean audio file names 
def name_clean():
    names = []
    for folder in folders:
        for file in os.listdir(folder):
            file = os.path.join(folder, file)
            new_name = file.replace(" ", "_")
            try:
                os.rename(file, new_name)
            except:
                ...
            names.append(new_name)
    
    with open("song_list.json", "w") as f:
        f.write(json.dumps(names, indent=2))


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


def xml_clean(file_name = "all.xspf", playlist_title = "Playlist"):
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

    title_tag.text = playlist_title
    tree.write(f"playlists/{file_name}", pretty_print=True, xml_declaration=True, encoding="UTF-8")
    
    #writing m3u local files
    with open(f"playlists/{file_name.split('.')[0]}.m3u", 'w') as fo:
        fo.write(xspf_to_m3u(root, ns, playlist_title))

    print(f"{file_name} Local XSPF and m3u Cleaned and written")

    # File location edit for server files 
    for location_tag in root.xpath("//default:location", namespaces=ns):
        location_tag.text = location_tag.text.replace("../", "https://raw.githubusercontent.com/raccess21/Audio/main/")
        
    # Write web files
    title_tag.text = playlist_title + " Web"
    tree.write(f"playlists web/{file_name.split('.')[0]} web.xspf", pretty_print=True, xml_declaration=True, encoding="UTF-8")
    
    with open(f"playlists web/{file_name.split('.')[0]} web.m3u", 'w') as fo:
        fo.write(xspf_to_m3u(root, ns, playlist_title + " Web"))
    print(f"{file_name} Web XSPF and m3u Cleaned and written")


def embed_lyrics(lyrics, file_name):
    audiofile = eyed3.load(file_name)
    try:
        audiofile.tag
    except AttributeError:
        audiofile.initTag()
    # audiofile.tag.lyrics.set(lyrics)
    # audiofile.tag.save()
    print(audiofile.tag)

def create_xml():
    ...
    
def main():
    for file_name in os.listdir("playlists temp"):
        playlist_title = file_name.split('.xspf')[0].strip()
        # name_clean()
        xml_clean(file_name, playlist_title)
        # create_xml()
        # ...
        # embed_lyrics("[00:43.22]lala", "Asi_Gabru_Punjabi_-_Amrinder_Gill.m4a")

    # remove_tags(tree=1, tags=["duration", "extension"])

if __name__ == "__main__":
    main()