# Article Generator vs News Summarizer

## Overview

The **Article Generator** is a reusable, role-based evolution of the **News Summarizer** that provides greater flexibility and broader applicability.

## Key Improvements

### 1. **Role Flexibility**
- **News Summarizer**: Fixed as "world-class news analyst"
- **Article Generator**: 10+ configurable professional roles + custom roles

### 2. **Content Scope**
- **News Summarizer**: Optimized for news articles
- **Article Generator**: Any document type (scientific papers, financial reports, policies, etc.)

### 3. **Output Format**
- **News Summarizer**: Summary + key points + topics
- **Article Generator**: Full structured articles with sections, introduction, conclusion

### 4. **Customization**
- **News Summarizer**: Fixed summary lengths (short/medium/detailed)
- **Article Generator**: Configurable style, audience, length, focus areas, and role

### 5. **Use Cases**
- **News Summarizer**: News aggregation and monitoring
- **Article Generator**: Content creation, analysis, reporting across domains

## Feature Comparison

| Feature | News Summarizer | Article Generator |
|---------|----------------|-------------------|
| **Professional Roles** | 1 (News Analyst) | 11+ (Configurable) |
| **Custom Roles** | ❌ | ✅ |
| **Article Styles** | N/A | 4 (formal, conversational, technical, persuasive) |
| **Target Audience** | General | Configurable |
| **Focus Areas** | N/A | Configurable |
| **Output Type** | Summary | Full Article |
| **Section Structure** | ❌ | ✅ (Introduction, Sections, Conclusion) |
| **Digest Generation** | ✅ | ✅ (Enhanced) |
| **Social Media Posts** | ✅ | ❌ (Can be added) |
| **Interactive Q&A** | ✅ | ✅ |
| **Document Types** | News URLs | Any (PDF, URLs, docs, videos, etc.) |
| **Export Formats** | Markdown | Markdown + JSON |

## Code Comparison

### News Summarizer
```python
from tools.news_tracker.news_summarizer import NewsSummarizer

summarizer = NewsSummarizer()
summarizer.initialize(
    news_urls=['https://news-site.com/article'],
    summary_length="medium"
)
summaries = summarizer.get_summaries()
digest = summarizer.get_digest()
```

### Article Generator
```python
from tools.article_generator import ArticleGenerator, ArticleRole

generator = ArticleGenerator()
generator.initialize(
    documents=['report.pdf', 'https://article.com'],
    role=ArticleRole.FINANCIAL_ADVISOR,  # Or any other role
    article_style="formal",
    target_audience="investment professionals",
    article_length="medium",
    focus_areas="market trends, risks"
)
articles = generator.get_articles()
digest = generator.get_digest()
```

## Migration Guide

### Converting News Summarizer Code to Article Generator

**Before (News Summarizer):**
```python
summarizer = NewsSummarizer()
summarizer.initialize(
    news_urls=['https://news.com/article1', 'https://news.com/article2'],
    summary_length="medium"
)
summaries = summarizer.get_summaries()
digest = summarizer.get_digest()

for summary in summaries:
    print(summary['title'])
    print(summary['summary'])
    print(summary['key_points'])
```

**After (Article Generator):**
```python
generator = ArticleGenerator()
generator.initialize(
    documents=['https://news.com/article1', 'https://news.com/article2'],
    role=ArticleRole.JOURNALIST,  # Equivalent to news analyst
    article_length="medium"
)
articles = generator.get_articles()
digest = generator.get_digest()

for article in articles:
    print(article['title'])
    print(article['introduction'])
    print(article['key_insights'])
```

## When to Use Each

### Use News Summarizer When:
- ✅ Specifically working with news articles
- ✅ Need social media post generation
- ✅ Want quick summaries (not full articles)
- ✅ News monitoring and aggregation workflows

### Use Article Generator When:
- ✅ Working with diverse document types
- ✅ Need role-specific perspectives
- ✅ Creating full-length articles
- ✅ Require customizable output styles
- ✅ Analyzing financial, scientific, or business documents
- ✅ Need professional-grade content creation

## Architecture Similarity

Both extend `BaseWorkFlow` and share:
- Document loading via `DocumentImporter`
- RAG-based retrieval
- LangGraph workflow integration
- Interactive Q&A capabilities
- Digest generation

## Example Use Cases

### News Summarizer
```python
# Daily news digest
summarizer.initialize(
    news_urls=[
        'https://news.com/tech1',
        'https://news.com/tech2'
    ],
    summary_length="short"
)
digest = summarizer.get_digest()

# Social media post
post = summarizer.create_social_media_post(
    platform="twitter",
    summary_index=0
)
```

### Article Generator
```python
# Financial report analysis
generator.initialize(
    documents=['Q4-2024-earnings.pdf'],
    role=ArticleRole.FINANCIAL_ADVISOR,
    target_audience="investors",
    focus_areas="revenue growth, market position"
)

# Scientific paper summary
generator.initialize(
    documents=['research-paper.pdf'],
    role=ArticleRole.SCIENTIFIC_RESEARCHER,
    article_style="technical",
    target_audience="researchers"
)

# Business strategy content
generator.initialize(
    documents=['market-analysis.pdf', 'competitor-report.pdf'],
    role=ArticleRole.BUSINESS_ANALYST,
    article_style="persuasive",
    target_audience="executives"
)
```

## Performance Considerations

- **News Summarizer**: Optimized for shorter news articles, faster processing
- **Article Generator**: Handles longer documents, generates more comprehensive output

## Future Enhancements

Both modules could be enhanced with:
- Multi-language support
- Image/chart extraction
- Citation management
- Version comparison
- Collaborative editing

## Recommendation

- **Keep News Summarizer** for dedicated news monitoring workflows
- **Use Article Generator** for general-purpose article generation and analysis
- **Both can coexist** - they serve different but complementary purposes
