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


def xml_clean(file_name = "all.xspf", playlist_title = "Playlist"):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(file_name, parser)
    root = tree.getroot()
    
    # Define namespaces
    ns = {
        'default': "http://xspf.org/ns/0/",
        'vlc': "http://www.videolan.org/vlc/playlist/ns/0/"
    }
    
    root.xpath("//default:title", namespaces=ns)[0].text = playlist_title

    # remove unnecessary tags from track data
    for track in root.xpath("//default:track", namespaces=ns):
        image_tag = track.find("default:image", namespaces=ns)
        if image_tag is not None:
            track.remove(image_tag)
        
        annotation_tag = track.find("default:annotation", namespaces=ns)
        if annotation_tag is not None:
            track.remove(annotation_tag)
        

    # File location edit for local files 
    for location_tag in root.xpath("//default:location", namespaces=ns):
        location_tag.text = location_tag.text.replace("file:///C:/rahul/Audio/", "")

    tree.write(file_name, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"Cleaned XSPF written to {file_name}")


    # File location edit for server files 
    for location_tag in root.xpath("//default:location", namespaces=ns):
        location_tag.text = location_tag.text.replace(
                "file:///C:/rahul/Audio/files/", 
                "https://raw.githubusercontent.com/raccess21/Audio/main/files/"
            )

    # Write the modified XML to a new file
    file_name = f"{file_name.split('.')[0]}_web.xspf"
    tree.write(file_name, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"Cleaned web XSPF written to {file_name}")


def main():
    name_clean()
    xml_clean(file_name="all_songs.xspf", playlist_title="All Songs")

if __name__ == "__main__":
    main()