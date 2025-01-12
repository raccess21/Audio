import os
import json
import chardet
from lxml import etree

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


def remove_tags(tree, tags, ns):
    if not isinstance(tags, list):
        tags = [tags]

    parser = etree.XMLParser(remove_blank_text=True)
    root = tree.getroot()
        
    for tag in tags:
        # Find all instances of the tag using XPath with namespace
        elements = root.xpath(f".//default:{tag}", namespaces=ns)
        for element in elements:
            # Remove each found element
            element.getparent().remove(element)

    

def xml_clean_vlc(file_name = "all.xspf", playlist_title = "Playlist"):
    # Define namespaces
    ns = {
        'default': "http://xspf.org/ns/0/",
    }
    
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(f"playlists temp/{file_name}", parser)
    root = tree.getroot()
    
    title_tag = root.xpath("//default:title", namespaces=ns)[0]

    # remove unnecessary tags from track data
    bad_tags = ["image", "annotation", "extension"]    
    remove_tags(tree, bad_tags, ns)

    # File location edit for local files hard path 
    tree.write(f"playlists temp2/{file_name}", pretty_print=True, xml_declaration=True, encoding="UTF-8")

    # File location edit for local files relative paths
    for location_tag in root.xpath("//default:location", namespaces=ns):
        location_tag.text = location_tag.text.replace("file:///C:/rahul/Audio/", "../")

    title_tag.text = playlist_title
    tree.write(f"playlists/{file_name}", pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"{file_name} XSPF Cleaned and written")


    # File location edit for server files 
    for location_tag in root.xpath("//default:location", namespaces=ns):
        location_tag.text = location_tag.text.replace("../", "https://raw.githubusercontent.com/raccess21/Audio/main/")

    # Write the modified XML to a new file
    title_tag.text = playlist_title + " Web"
    file_name = f"{file_name.split('.')[0]}_web.xspf"
    tree.write(f"playlists web/{file_name}", pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"{file_name} XSPF Cleaned and written web")


def create_xml():
    ...
    
def main():
    file_names = [
        "The Wall - Pink Floyd (flac).xspf",
        "all_songs.xspf",
        "Dark Side of the Moon - Pink Floyd (MP3).xspf"
    ]

    for file_name in file_names:
        playlist_title = file_name.split('.xspf')[0].strip()
        # name_clean()
        xml_clean_vlc(file_name, playlist_title)
        # create_xml()
        # ...
    # remove_tags(tree=1, tags=["duration", "extension"])

if __name__ == "__main__":
    main()