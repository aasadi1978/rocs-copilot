# Article Generator

A reusable, role-based article generation agent that can analyze documents and create professional articles from different expert perspectives.

## Overview

The Article Generator is inspired by `news_summarizer.py` but designed to be more flexible and reusable. It can generate articles on any topic (news, scientific research, financial reports, etc.) by adopting different professional roles.

## Features

- **Configurable Professional Roles**: Choose from 10+ predefined roles or define custom roles
- **Multiple Document Types**: Supports URLs, PDFs, Word docs, videos, and more
- **Structured Output**: Generates well-formatted articles with sections, insights, and tags
- **Digest Generation**: Creates comprehensive digests from multiple articles
- **Interactive Q&A**: Built-in chat interface for querying documents
- **Flexible Export**: Save as Markdown or JSON

## Installation

The module is part of the `rocs-copilot` backend. Make sure you have the required dependencies installed:

```bash
pip install -e .
```

## Quick Start

### Basic Usage

```python
from tools.article_generator import ArticleGenerator, ArticleRole

# Create generator with a professional role
generator = ArticleGenerator()
generator.initialize(
    documents=['report.pdf', 'https://article-url.com'],
    role=ArticleRole.FINANCIAL_ADVISOR,
    article_style="formal",
    target_audience="investment professionals"
)

# Get generated articles
articles = generator.get_articles()

# Save to file
generator.save_articles_to_file('output.md', format='markdown')

# Generate digest
digest = generator.get_digest()
print(digest)
```

## Available Roles

### Predefined Roles

The `ArticleRole` enum provides these professional roles:

1. **FINANCIAL_ADVISOR** - Financial analysis and investment insights
2. **JOURNALIST** - News reporting and storytelling
3. **SCIENTIFIC_RESEARCHER** - Research analysis and academic writing
4. **BUSINESS_ANALYST** - Market analysis and strategic insights
5. **TECHNICAL_WRITER** - Technical documentation and explanations
6. **MARKETING_SPECIALIST** - Content marketing and brand storytelling
7. **POLICY_ANALYST** - Policy analysis and regulatory insights
8. **HEALTHCARE_EXPERT** - Medical and healthcare information
9. **LEGAL_ANALYST** - Legal analysis and implications
10. **EDUCATOR** - Educational content and learning materials
11. **CUSTOM** - Define your own role

### Using Custom Roles

#### Method 1: Using ArticleRole.CUSTOM

```python
custom_description = """You are a senior supply chain strategist with 20+ years 
of experience in logistics optimization and global trade."""

generator.initialize(
    documents=['supply-chain-report.pdf'],
    role=ArticleRole.CUSTOM,
    custom_role_description=custom_description,
    article_style="persuasive",
    target_audience="supply chain executives"
)
```

#### Method 2: Using String Shorthand

```python
# Just pass the role as a string - it will be auto-converted
generator.initialize(
    documents=['data-science-paper.pdf'],
    role="data scientist",  # Will create custom role automatically
    article_style="technical",
    target_audience="ML practitioners"
)
```

## Configuration Options

### Article Styles

- **formal**: Professional tone with precise language
- **conversational**: Engaging, reader-friendly tone
- **technical**: Detailed with technical terminology
- **persuasive**: Compelling arguments and calls to action

### Article Lengths

- **short**: 500-800 words
- **medium**: 1000-1500 words
- **long**: 2000-3000 words

### Complete Example

```python
from tools.article_generator import ArticleGenerator, ArticleRole

generator = ArticleGenerator()
generator.initialize(
    documents=[
        'https://example.com/article1',
        'path/to/report.pdf',
        'path/to/docs/'  # Entire directory
    ],
    role=ArticleRole.BUSINESS_ANALYST,
    article_style="formal",
    target_audience="C-suite executives",
    article_length="medium",
    focus_areas="competitive analysis, market opportunities",
    chunk_size=2000,
    chunk_overlap=200
)

# Get all articles
articles = generator.get_articles()

# Format as markdown
for article in articles:
    print(generator.format_article_as_markdown(article))

# Generate digest with specific focus
digest = generator.get_digest(
    digest_focus="strategic opportunities and risk factors"
)

# Save outputs
generator.save_articles_to_file('articles.md', format='markdown')
generator.save_articles_to_file('articles.json', format='json')

# Interactive Q&A
generator.display_state_graph(graph_name="my_workflow")
result = generator.invoke_chat([{
    "role": "user",
    "content": "What are the main insights?"
}])
print(result["messages"][-1].content)
```

## Article Structure

Each generated article includes:

- **title**: Compelling article title
- **introduction**: Engaging opening paragraph(s)
- **main_sections**: List of sections with headings and content
- **conclusion**: Closing thoughts and takeaways
- **key_insights**: 3-5 main insights (bullet points)
- **tags**: Relevant topic keywords
- **metadata**: Source, role, style, audience info

## Advanced Usage

### Multiple Document Analysis

```python
generator.initialize(
    documents=[
        'financial_report_q1.pdf',
        'financial_report_q2.pdf',
        'market_analysis.pdf'
    ],
    role=ArticleRole.FINANCIAL_ADVISOR,
    target_audience="investors",
    focus_areas="quarterly trends, growth opportunities"
)

# Generate comprehensive digest
digest = generator.get_digest(
    digest_focus="year-over-year trends and investment implications"
)
```

### Streaming Chat Interface

```python
# Build graph first
generator.display_state_graph(graph_name="chat_workflow")

# Stream responses
for node, message in generator.stream_chat([
    {"role": "user", "content": "Explain the main findings"}
]):
    print(f"{node}: {message.content}")
```

## Examples

See `run_article_generator.py` for complete examples:

1. Financial Advisor analyzing economic reports
2. Journalist writing news articles
3. Scientific Researcher analyzing research papers
4. Custom supply chain expert role
5. Multiple document business analysis
6. Interactive Q&A sessions

Run examples:

```bash
cd backend/tools/article_generator
python run_article_generator.py
```

## Comparison with News Summarizer

| Feature | News Summarizer | Article Generator |
|---------|----------------|-------------------|
| **Purpose** | Summarize news articles | Generate professional articles |
| **Roles** | Fixed (news analyst) | 10+ configurable roles |
| **Output** | Summary + key points | Full structured articles |
| **Document Types** | News URLs | Any document type |
| **Customization** | Limited | Highly customizable |
| **Use Cases** | News aggregation | Analysis, reporting, content creation |

## API Reference

### ArticleGenerator Class

#### `initialize(**kwargs)`

Initialize the generator with documents and configuration.

**Parameters:**
- `documents` (List[str|Path]): Document sources
- `role` (ArticleRole|str): Professional role
- `custom_role_description` (str, optional): Custom role description
- `article_style` (str): Writing style
- `target_audience` (str): Intended audience
- `article_length` (str): Desired length
- `focus_areas` (str, optional): Specific focus areas
- `chunk_size` (int): Document chunk size
- `chunk_overlap` (int): Chunk overlap

#### `get_articles() -> List[Dict]`

Returns all generated articles.

#### `get_digest(digest_focus: str) -> str`

Generates comprehensive digest from articles.

#### `save_articles_to_file(output_path, format="markdown")`

Saves articles to file (markdown or json).

#### `format_article_as_markdown(article: Dict) -> str`

Formats single article as markdown.

## Best Practices

1. **Choose the Right Role**: Match the role to your document type and audience
2. **Set Appropriate Length**: Short for summaries, long for in-depth analysis
3. **Use Focus Areas**: Guide the article generation to specific topics
4. **Batch Similar Documents**: Process related documents together for better digests
5. **Leverage Chat**: Use the Q&A interface for iterative refinement

## Troubleshooting

### No articles generated
- Check that documents are accessible
- Verify document format is supported
- Check logs for loading errors

### Articles lack depth
- Increase `article_length` parameter
- Add specific `focus_areas`
- Ensure source documents have sufficient content

### Custom role not working
- Provide detailed `custom_role_description`
- Include expertise areas and perspective

## Contributing

To add new predefined roles:

1. Add to `ArticleRole` enum in `article_prompts.py`
2. Add role definition to `ROLE_DEFINITIONS` dict
3. Update README with new role

## License

Part of the rocs-copilot project.
