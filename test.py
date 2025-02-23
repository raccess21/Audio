from info import all_tags, all_files_in, music_extensions, file_name_ext, audio_tags
from langdetect import detect
from mutagen.id3 import TCON

def lang_detect(file):
        langs = {
            "hi": "Hindi", "en": "English", "ost": "Soundtrack"
        }
        
        name, ext = file_name_ext(file)
        
        if ext != "lrc":
            return False
        
        with open(file, "r", encoding='UTF-8') as fi:
            data = fi.read()
            if data:
                try:
                    lang = detect(data)
                    if lang != "en":
                        lang = "hi"
                except:
                    lang = "ost"
        print(lang)
        return langs[lang]

music = music_extensions()

for file in all_files_in("lossy/"):
    name, ext = file_name_ext(file)

    if ext in music:
        print(name, end=": ")
        tags = audio_tags()[ext]
        audio = tags["function"](file)
        lang = lang_detect(file.split("." + ext)[0] + ".lrc")
        
        try:
            if ext == "mp3":
                current = audio[tags["genre"]].text
                if lang not in current:
                    current.append(lang)
                audio[tags["genre"]] = TCON(encoding=3, text=current)

            elif ext == "m4a" or ext == "flac":
                current = audio[tags["genre"]]
                if lang not in current:
                    current.append(lang)
                audio[tags["genre"]] = current
            
            audio.save()
        
        except Exception as e:
            print(file, e)

