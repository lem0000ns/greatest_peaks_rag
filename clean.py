from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

def semantic_group(content: str, model_name: str):
    embeddings = OpenAIEmbeddings(model=model_name)
    text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")
    groups = text_splitter.split_text(content)
    return groups

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
    for file_name in file_names:
        with open(f"data/original/{file_name}", "r") as file:
            content = file.read()
        if content[0] != '[':
            print(f"{file_name} has already been cleaned or is in unexpected format (should start with [)")
            continue
        cleaned_content = semantic_group(clean_content(content), "sentence-transformers/all-MiniLM-L6-v2")
        with open(f"data/cleaned/{file_name}", "w") as file:
            for i, group in enumerate(cleaned_content):
                file.write(group.strip() + "\n\n")

if __name__ == "__main__":
    clean_text_files()