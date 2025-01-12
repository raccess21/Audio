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
    

    songs = []
    # File location edit for server files 
    for location_tag in root.xpath("//default:location", namespaces=ns):
        songs.append(location_tag.text)
        location_tag.text = location_tag.text.replace("../", "https://raw.githubusercontent.com/raccess21/Audio/main/")
        
    # Write the modified XML to a new file
    title_tag.text = playlist_title + " Web"
    tree.write(f"playlists web/{file_name.split('.')[0]} web.xspf", pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"{file_name} Web and local XSPF Cleaned and written")
    
    with open(f"playlists/{file_name.split('.')[0]}.m3u", 'w') as fo:
        fo.write("\n".join(songs))
    
    print(f"{file_name} Local m3u cleaned and written.")

#def xsfp_process(file_name = "all.xspf", playlist_title = "Playlist"):

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