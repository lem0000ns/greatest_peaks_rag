from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
import argparse

FILE_NAMES = ["bird.txt", "curry.txt", "duncan.txt", "durant.txt", "garnett.txt", "hakeem.txt", "jordan.txt", "kareem.txt", "kobe.txt", "lebron.txt", "magic.txt", "robinson.txt", "russell.txt", "shaq.txt", "walton.txt"]

# group into semantically coherent paragraphs for downstream chunking
def semantic_group():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile", breakpoint_threshold_amount=80)
    for file_name in FILE_NAMES:
        with open(f"data/3_sentences/{file_name}", "r") as file:
            content = file.read()
        groups = text_splitter.split_text(content)
        with open(f"data/4_groups/{file_name}", "w") as file:
            for group in groups:
                file.write(group.strip() + "\n\n")

def clean_text_files():
    for file_name in FILE_NAMES:
        with open(f"data/1_original/{file_name}", "r") as file:
            content = file.read()
        if content[0] != '[' or content[0].isupper():
            print(f"{file_name} has already been cleaned or is in unexpected format (should start with [)")
            continue

        def clean_content(content: str):
            no_annotations_content = []
            for i, line in enumerate(content.split("\n")):
                # remove timestamp
                line = line.split("]")[1].strip()
                # remove non-speech annotations like [Music], [Applause], etc.
                if line == '' or line[0] == '[':
                    continue
                no_annotations_content.append(line)
            return no_annotations_content

        cleaned_content = clean_content(content)
        with open(f"data/2_cleaned/{file_name}", "w") as file:
            for group in cleaned_content:
                file.write(group.strip() + "\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="clean")
    args = parser.parse_args()
    if args.mode == "clean":
        clean_text_files()
    elif args.mode == "group":
        semantic_group()
    else:
        raise ValueError(f"Invalid mode: {args.mode}")