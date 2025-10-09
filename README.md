# NBA Players RAG

A Retrieval-Augmented Generation (RAG) system that allows you to query and get insights from Harry Potter related lore, cited from hp-lexicon.org

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the project root with your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Store all relevant documents in vector database:**

   ```bash
   python store_db.py
   ```

4. **Initiate conversation with Harry Potter knowledge-infused chatbot!**

```bash
python search.py"
```

BeautifulSoup + requests utilized for mass document scraping from hp-lexicon.org. ChromaDB used for vector storage and OpenAI embeddings for semantic search, retrieving the most relevant content chunks to answer relevant questions. SerperAPI used as a fallback in case RAG can't answer user query.
