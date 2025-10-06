from langchain_community.document_loaders import WikipediaLoader
from langchain.schema import Document

input_players = ""

# load wikipedia data for each player
def get_wiki_data(players):
    rag_docs = []
    for player in players:
        try:    
            loader = WikipediaLoader(query=player, load_max_docs=1, doc_content_chars_max=100000)
            wiki_doc = loader.load()
            rag_docs.extend(wiki_doc)
        except Exception as e:
            print(f"Error loading Wikipedia data for {player}: {e}")
            continue
    return rag_docs
# store the wikipedia data in a file
def store_wiki_data_in_file(rag_docs):
    for doc in rag_docs:
        print('$' * 100)
        print(doc)
        print('$' * 100)
        with open(f"data/{doc.metadata['title']}.txt", "w") as f:
            f.write(doc.page_content)


if __name__ == "__main__":
    players = []
    count = 0
    player_string = input("Enter at most 10 NBA players, separated by commas: ")
    input_players = player_string
    players = player_string.split(",")
    rag_docs = get_wiki_data(players)
    store_wiki_data_in_file(rag_docs)