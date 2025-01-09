import os
import json
import chardet

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



def tag_remove(tag_names, xml_data):
    if not isinstance(tag_names, list):
        tag_names = [tag_names]

    for tag_name in tag_names:
        xml_data = xml_data.replace(f"</{tag_name}>", f"<{tag_name}>")
        xml_data = "".join([val for i, val in enumerate(xml_data.split(f"<{tag_name}>")) if i % 2 == 0])
    
    return "\n".join([line for line in xml_data.splitlines() if line.strip()])


def encoding_check(file_name):
    with open(file_name, 'rb') as f:
        return chardet.detect(f.read())["encoding"]

def xml_clean():
    bad_tag_names = [
        "image",
        "annotation",
    ]

    for file in os.listdir():
        if file.endswith("t.xspf"):
            encoding = encoding_check(file)

            with open(file, "r", encoding=encoding) as f:
                xml_data = f.read()

            xml_data = tag_remove(bad_tag_names, xml_data)
            
            file = file.split(".")[0]
            with open(f"{file}.xspf", "w", encoding=encoding) as f:
                f.write(xml_data.replace(
                    "file:///C:/rahul/Audio/", 
                    ""
                ))

            with open(f"{file}_web.xspf", "w", encoding=encoding) as f:
                f.write(xml_data.replace(
                    "file:///C:/rahul/Audio/files/", 
                    "https://raw.githubusercontent.com/raccess21/Audio/main/files/"
                ))


def main():
    name_clean()
    xml_clean()


if __name__ == "__main__":
    main()