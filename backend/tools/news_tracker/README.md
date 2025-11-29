# News Tracker Agent

A streamlined news summarization agent that **leverages your existing RAG infrastructure** instead of duplicating functionality.

## Key Design Principle

✅ **Reuses existing RAG components**:
- `DocLoader` from `tools.rag.doc_loader` - loads URLs
- `load_url.py` - extracts web content  
- Existing caching and document processing

✅ **Adds news-specific value**:
- `NewsSummarizer` - generates summaries, key points, topics
- News digest generation
- Query interface for news content

## Architecture

```
News Tracker
├── news_workflow.py     (uses DocLoader from RAG)
├── news_summarizer.py   (adds news-specific summarization)
└── init_news_tracker.py (example usage)

Leverages:
└── tools/rag/
    ├── doc_loader.py       (reused)
    ├── load_url.py         (reused)
    └── document_repository.py (reused)
```

## Quick Start

```python
from tools.news_tracker.news_workflow import NEWS_TRACKER_INSTANCE

# Your news list
news_list = [
    "https://techcrunch.com/latest-ai-news",
    "https://www.reuters.com/technology/",
]

# Initialize (uses existing RAG DocLoader)
NEWS_TRACKER_INSTANCE.initialize(
    news_urls=news_list,
    summary_length="medium"
)

# Get summaries
summaries = NEWS_TRACKER_INSTANCE.get_summaries()

# Get digest
digest = NEWS_TRACKER_INSTANCE.get_digest()
print(digest)

# Query the news
answer = NEWS_TRACKER_INSTANCE.query_news("What's the main tech news?")
```

## What's Different from RAG?

| RAG Workflow | News Tracker |
|--------------|--------------|
| Q&A with document retrieval | News summarization |
| Vector embeddings + retrieval tool | Direct summarization |
| Agentic decision-making | Batch processing |
| Uses: `Retriever`, `grade_documents` | Uses: `DocLoader` only |

## Benefits of Reusing RAG Infrastructure

1. **No code duplication** - URL loading handled by existing `load_url.py`
2. **Consistent behavior** - Same URL parsing logic as RAG
3. **Caching works** - Leverages `DocumentRepository` cache
4. **Maintainability** - One place to fix URL loading issues
5. **Smaller footprint** - Only adds summarization logic

## Files Created

- `news_workflow.py` - Main workflow (60 lines lighter by reusing RAG)
- `news_summarizer.py` - LLM-based summarization and digest generation
- `init_news_tracker.py` - Example usage

## Usage Example

```bash
# Run the example
python -m backend.tools.news_tracker.init_news_tracker
```

## API Reference

### `NEWS_TRACKER_INSTANCE.initialize(news_urls, summary_length="medium")`
Initialize with news URLs using existing RAG DocLoader.

### `NEWS_TRACKER_INSTANCE.get_summaries()`
Returns list of article summaries with key points and topics.

### `NEWS_TRACKER_INSTANCE.get_digest()`
Generates a comprehensive news digest combining all articles.

### `NEWS_TRACKER_INSTANCE.query_news(query)`
Answer questions about the loaded news.

## Summary Lengths

- `"short"` - 2-3 sentences
- `"medium"` - 1 paragraph (default)
- `"detailed"` - Multiple paragraphs

## Dependencies

All dependencies already satisfied by your RAG package!
- Uses existing `DocLoader`, `load_url`, `Document`
- Adds only: news-specific LLM prompts
