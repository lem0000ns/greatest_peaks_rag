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

3. **Build the vector database:**
   ```bash
   python store_db.py
   ```

### Querying the RAG System

**Basic query:**

```bash
python query_data.py --query "What makes Stephen Curry one of the greatest offensive players ever?"
```

### Data Processing Pipeline

1. **Original transcripts** → `data/1_original/`
2. **Cleaned data** → `data/2_cleaned/`
3. **Sentence-segmented** → `data/3_sentences/`
4. **Grouped content** → `data/4_groups/` (used for RAG)

The system uses ChromaDB for vector storage and OpenAI embeddings for semantic search, retrieving the most relevant content chunks to answer your questions about basketball peaks and analysis.
