# Article Generator - Quick Reference Guide

## Installation & Import

```python
from tools.article_generator import ArticleGenerator, ArticleRole
```

## Basic Patterns

### Pattern 1: Single Document, Predefined Role

```python
generator = ArticleGenerator()
generator.initialize(
    documents=['report.pdf'],
    role=ArticleRole.FINANCIAL_ADVISOR
)
articles = generator.get_articles()
```

### Pattern 2: Multiple Documents with Configuration

```python
generator = ArticleGenerator()
generator.initialize(
    documents=['doc1.pdf', 'doc2.pdf', 'https://url.com'],
    role=ArticleRole.JOURNALIST,
    article_style="conversational",
    target_audience="general public",
    article_length="medium",
    focus_areas="key findings, practical implications"
)
```

### Pattern 3: Custom Role

```python
generator = ArticleGenerator()
generator.initialize(
    documents=['analysis.pdf'],
    role=ArticleRole.CUSTOM,
    custom_role_description="You are an AI ethics expert...",
    article_style="formal"
)
```

### Pattern 4: Custom Role Shorthand

```python
generator = ArticleGenerator()
generator.initialize(
    documents=['paper.pdf'],
    role="data scientist",  # Auto-creates custom role
    article_style="technical"
)
```

## Common Tasks

### Save Articles to File

```python
# Markdown
generator.save_articles_to_file('output.md', format='markdown')

# JSON
generator.save_articles_to_file('output.json', format='json')
```

### Generate and Save Digest

```python
digest = generator.get_digest(
    digest_focus="investment opportunities"
)

with open('digest.md', 'w', encoding='utf-8') as f:
    f.write(digest)
```

### Format Single Article

```python
articles = generator.get_articles()
markdown = generator.format_article_as_markdown(articles[0])
print(markdown)
```

### Interactive Q&A

```python
# Build graph
generator.display_state_graph(graph_name="workflow")

# Ask questions
result = generator.invoke_chat([{
    "role": "user",
    "content": "What are the key findings?"
}])
print(result["messages"][-1].content)
```

## All Available Roles

```python
ArticleRole.FINANCIAL_ADVISOR      # Financial analysis
ArticleRole.JOURNALIST             # News writing
ArticleRole.SCIENTIFIC_RESEARCHER  # Research analysis
ArticleRole.BUSINESS_ANALYST       # Business insights
ArticleRole.TECHNICAL_WRITER       # Technical docs
ArticleRole.MARKETING_SPECIALIST   # Marketing content
ArticleRole.POLICY_ANALYST         # Policy analysis
ArticleRole.HEALTHCARE_EXPERT      # Healthcare info
ArticleRole.LEGAL_ANALYST          # Legal analysis
ArticleRole.EDUCATOR               # Educational content
ArticleRole.CUSTOM                 # Define your own
```

## Configuration Options

### Article Styles
- `"formal"` - Professional, precise
- `"conversational"` - Engaging, friendly
- `"technical"` - Detailed, technical
- `"persuasive"` - Compelling arguments

### Article Lengths
- `"short"` - 500-800 words
- `"medium"` - 1000-1500 words
- `"long"` - 2000-3000 words

## Complete Example

```python
from pathlib import Path
from tools.article_generator import ArticleGenerator, ArticleRole

# Initialize
generator = ArticleGenerator()
generator.initialize(
    documents=[
        Path('reports/q4-2024.pdf'),
        'https://industry-news.com/article',
        Path('research/')  # Entire directory
    ],
    role=ArticleRole.BUSINESS_ANALYST,
    article_style="formal",
    target_audience="C-suite executives",
    article_length="medium",
    focus_areas="market trends, competitive analysis",
    chunk_size=2000,
    chunk_overlap=200
)

# Get articles
articles = generator.get_articles()
print(f"Generated {len(articles)} articles")

# Save outputs
generator.save_articles_to_file('articles.md', format='markdown')
generator.save_articles_to_file('articles.json', format='json')

# Generate digest
digest = generator.get_digest(
    digest_focus="strategic opportunities and risks"
)

with open('digest.md', 'w', encoding='utf-8') as f:
    f.write(digest)

# Interactive Q&A
generator.display_state_graph(graph_name="my_workflow")
result = generator.invoke_chat([{
    "role": "user",
    "content": "Summarize the main findings"
}])
print(result["messages"][-1].content)
```

## Article Structure

Each article contains:

```python
{
    'title': str,
    'introduction': str,
    'main_sections': [
        {'heading': str, 'content': str},
        ...
    ],
    'conclusion': str,
    'key_insights': [str, str, ...],
    'tags': str,
    'metadata': {
        'source': str,
        'role': str,
        'style': str,
        'audience': str
    }
}
```

## Tips

1. **Match role to content**: Use FINANCIAL_ADVISOR for financial docs, SCIENTIST for research papers
2. **Set focus areas**: Guide generation to specific topics of interest
3. **Use appropriate length**: Short for summaries, long for deep analysis
4. **Batch related docs**: Process similar documents together for coherent digests
5. **Leverage Q&A**: Use chat interface for follow-up questions

## Common Use Cases

### Financial Report Analysis
```python
role=ArticleRole.FINANCIAL_ADVISOR
article_style="formal"
target_audience="investors"
focus_areas="returns, risks, opportunities"
```

### News Article Creation
```python
role=ArticleRole.JOURNALIST
article_style="conversational"
target_audience="general public"
article_length="medium"
```

### Research Paper Summary
```python
role=ArticleRole.SCIENTIFIC_RESEARCHER
article_style="technical"
target_audience="researchers"
focus_areas="methodology, findings, implications"
```

### Business Strategy Content
```python
role=ArticleRole.BUSINESS_ANALYST
article_style="persuasive"
target_audience="executives"
focus_areas="competitive advantages, market opportunities"
```

### Technical Documentation
```python
role=ArticleRole.TECHNICAL_WRITER
article_style="technical"
target_audience="developers"
article_length="long"
```
