def clean_content(content: str):
    no_annotations_content = []
    for i, line in enumerate(content.split("\n")):
        # remove timestamp
        line = line.split("]")[1].strip()
        # remove non-speech annotations like [Music], [Applause], etc.
        if line == '' or line[0] == '[':
            continue
        no_annotations_content.append(line)
    paragraphs = []
    cur_paragraph = []
    for line in no_annotations_content:
        # append current paragraph to paragraphs every 6 sentences and also if the last sentence is at least 3 words
        if len(cur_paragraph) >= 6 and len(cur_paragraph[-1]) >= 3:
            paragraphs.append(" ".join(cur_paragraph))
            cur_paragraph = []
        cur_paragraph.append(line)
    # add last sentences
    paragraphs.append(" ".join(cur_paragraph))
    return "\n".join(paragraphs)

def clean_text_files():
    file_names = ["bird.txt", "curry.txt", "duncan.txt", "durant.txt", "garnett.txt", "hakeem.txt", "jordan.txt", "kareem.txt", "kobe.txt", "lebron.txt", "magic.txt", "robinson.txt", "russell.txt", "shaq.txt", "walton.txt"]
    for file_name in file_names[:1]:
        with open(f"data/{file_name}", "r") as file:
            content = file.read()
        if content[0] != '[':
            print("Content has already been cleaned")
            continue
        cleaned_content = clean_content(content)
        with open(f"data/{file_name}", "w") as file:
            file.write(cleaned_content)

if __name__ == "__main__":
    clean_text_files()