# Getting Started with Article Generator

## 5-Minute Quick Start

### Step 1: Import the Module

```python
from tools.article_generator import ArticleGenerator, ArticleRole
```

### Step 2: Create and Initialize

```python
generator = ArticleGenerator()
generator.initialize(
    documents=['path/to/your/document.pdf'],
    role=ArticleRole.BUSINESS_ANALYST
)
```

### Step 3: Get Your Articles

```python
articles = generator.get_articles()
print(articles[0]['title'])
print(articles[0]['introduction'])
```

That's it! You've generated your first article.

---

## Complete First Example

Here's a complete working example:

```python
from pathlib import Path
from tools.article_generator import ArticleGenerator, ArticleRole

# 1. Create the generator
generator = ArticleGenerator()

# 2. Initialize with your document(s)
generator.initialize(
    documents=[Path('docs/2025-FedEx-Global-Economic-Impact-Report.pdf')],
    role=ArticleRole.BUSINESS_ANALYST,
    article_style="formal",
    target_audience="business executives",
    article_length="medium"
)

# 3. Get the generated articles
articles = generator.get_articles()
print(f"Generated {len(articles)} article(s)")

# 4. Display the first article
print("\nFirst Article:")
print(f"Title: {articles[0]['title']}")
print(f"\nIntroduction:\n{articles[0]['introduction']}")
print(f"\nKey Insights:")
for insight in articles[0]['key_insights']:
    print(f"  - {insight}")

# 5. Save to file
generator.save_articles_to_file('my_first_article.md')
print("\n✓ Article saved to my_first_article.md")

# 6. Generate a digest (if you have multiple documents)
digest = generator.get_digest()
with open('digest.md', 'w', encoding='utf-8') as f:
    f.write(digest)
print("✓ Digest saved to digest.md")
```

---

## Try Different Roles

### Financial Analysis

```python
generator.initialize(
    documents=['financial-report.pdf'],
    role=ArticleRole.FINANCIAL_ADVISOR,
    target_audience="investors"
)
```

### News Article

```python
generator.initialize(
    documents=['https://news-site.com/article'],
    role=ArticleRole.JOURNALIST,
    article_style="conversational"
)
```

### Technical Writing

```python
generator.initialize(
    documents=['technical-spec.pdf'],
    role=ArticleRole.TECHNICAL_WRITER,
    article_style="technical",
    target_audience="developers"
)
```

### Custom Role

```python
generator.initialize(
    documents=['industry-report.pdf'],
    role="sustainability consultant",  # Auto-creates custom role
    article_style="persuasive"
)
```

---

## Working with Multiple Documents

```python
generator.initialize(
    documents=[
        'report1.pdf',
        'report2.pdf',
        'https://article-url.com',
        Path('documents/')  # Entire directory
    ],
    role=ArticleRole.BUSINESS_ANALYST,
    article_length="medium"
)

# Get all articles
articles = generator.get_articles()
print(f"Generated {len(articles)} articles from your documents")

# Generate a comprehensive digest
digest = generator.get_digest(
    digest_focus="key business trends and opportunities"
)
print(digest)
```

---

## Next Steps

### 1. Explore All Roles

Try different professional roles to see how the perspective changes:

```python
roles_to_try = [
    ArticleRole.FINANCIAL_ADVISOR,
    ArticleRole.JOURNALIST,
    ArticleRole.SCIENTIFIC_RESEARCHER,
    ArticleRole.BUSINESS_ANALYST,
    ArticleRole.TECHNICAL_WRITER,
    ArticleRole.MARKETING_SPECIALIST,
    ArticleRole.POLICY_ANALYST,
    ArticleRole.HEALTHCARE_EXPERT,
    ArticleRole.LEGAL_ANALYST,
    ArticleRole.EDUCATOR
]
```

### 2. Customize Output

Fine-tune the output to your needs:

```python
generator.initialize(
    documents=['document.pdf'],
    role=ArticleRole.BUSINESS_ANALYST,
    article_style="persuasive",        # formal | conversational | technical | persuasive
    target_audience="C-suite executives",
    article_length="long",              # short | medium | long
    focus_areas="competitive analysis, market opportunities, risk factors"
)
```

### 3. Interactive Q&A

Build a chat interface to ask questions:

```python
# Build the workflow graph
generator.display_state_graph(graph_name="my_workflow")

# Ask questions
result = generator.invoke_chat([{
    "role": "user",
    "content": "What are the key takeaways?"
}])
print(result["messages"][-1].content)

# Ask follow-up questions
result = generator.invoke_chat([{
    "role": "user",
    "content": "What are the implications for our industry?"
}])
print(result["messages"][-1].content)
```

### 4. Export in Different Formats

```python
# Save as Markdown
generator.save_articles_to_file('articles.md', format='markdown')

# Save as JSON for programmatic access
generator.save_articles_to_file('articles.json', format='json')

# Format individual article
article = generator.get_articles()[0]
markdown = generator.format_article_as_markdown(article)
print(markdown)
```

---

## Common Patterns

### Pattern 1: Quick Analysis

```python
# Analyze one document quickly
generator = ArticleGenerator()
generator.initialize(documents=['doc.pdf'], role=ArticleRole.JOURNALIST)
print(generator.get_articles()[0]['introduction'])
```

### Pattern 2: Professional Report

```python
# Create a professional report
generator = ArticleGenerator()
generator.initialize(
    documents=['data.pdf'],
    role=ArticleRole.BUSINESS_ANALYST,
    article_style="formal",
    article_length="long"
)
generator.save_articles_to_file('professional_report.md')
```

### Pattern 3: Batch Processing

```python
# Process multiple documents
from pathlib import Path

docs = list(Path('reports/').glob('*.pdf'))
generator = ArticleGenerator()
generator.initialize(documents=docs, role=ArticleRole.FINANCIAL_ADVISOR)
digest = generator.get_digest()
```

---

## Troubleshooting

### Issue: No articles generated

**Solution:** Check that your document path is correct and the file exists.

```python
doc_path = Path('your-document.pdf')
if doc_path.exists():
    print("✓ Document found")
else:
    print("✗ Document not found at:", doc_path.absolute())
```

### Issue: Articles lack detail

**Solution:** Increase article length and add focus areas.

```python
generator.initialize(
    documents=['doc.pdf'],
    role=ArticleRole.BUSINESS_ANALYST,
    article_length="long",  # Changed from "short"
    focus_areas="detailed analysis, specific recommendations"
)
```

### Issue: Custom role not working as expected

**Solution:** Provide a detailed role description.

```python
generator.initialize(
    documents=['doc.pdf'],
    role=ArticleRole.CUSTOM,
    custom_role_description="""You are a senior industry expert with 20 years 
    of experience in supply chain management and logistics optimization. You 
    provide strategic insights that help companies improve efficiency."""
)
```

---

## Run the Examples

The repository includes complete examples:

```bash
cd backend/tools/article_generator
python test_article_generator.py
```

Or run specific examples:

```bash
python run_article_generator.py
```

---

## Learn More

- **README.md** - Complete documentation
- **QUICK_REFERENCE.md** - Quick reference guide
- **COMPARISON.md** - Comparison with News Summarizer
- **run_article_generator.py** - Complete examples

---

## Support

If you encounter issues:

1. Check the logs for error messages
2. Verify document paths and accessibility
3. Ensure all dependencies are installed
4. Review the examples in `run_article_generator.py`

---

Happy article generating! 🚀
