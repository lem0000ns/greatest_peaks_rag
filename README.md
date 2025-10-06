# "Greatest Peaks" RAG

A Retrieval-Augmented Generation (RAG) system that allows you to query and get insights from Ben Taylor's "Greatest Peaks" basketball analysis series.

**Source:** https://www.youtube.com/watch?v=o9XbDCXLE94&list=PLtzZl14BrKjSMb4IFWSy0qh_nFGiy7PoZ

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

3. **Input NBA players or other topics of RAG discussion:**

   ```bash
   python get_data.py
   ```

4. **Store in vector database:**
   ```bash
   python store_db.py
   ```

### Querying the RAG System

**Basic query:**

```bash
python search.py --query "What makes Stephen Curry one of the greatest offensive players ever?"
```

ChromaDB used for vector storage and OpenAI embeddings for semantic search, retrieving the most relevant content chunks to answer relevant questions. SerperAPI used as a fallback in case RAG can't answer user query.
