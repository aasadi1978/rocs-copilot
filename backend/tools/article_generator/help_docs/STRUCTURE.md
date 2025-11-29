# Article Generator - Module Structure

```
backend/tools/article_generator/
│
├── __init__.py                      # Package initialization
│   └── Exports: ArticleGenerator, ArticleRole, generate_article_prompt
│
├── article_generator.py             # Main ArticleGenerator class
│   ├── Class: ArticleGenerator(BaseWorkFlow)
│   │   ├── Methods:
│   │   │   ├── initialize()                    # Setup with docs & role
│   │   │   ├── get_articles()                  # Get generated articles
│   │   │   ├── get_digest()                    # Generate digest
│   │   │   ├── format_article_as_markdown()    # Format as MD
│   │   │   ├── save_articles_to_file()         # Save to file
│   │   │   ├── generate_digest()               # Digest from articles
│   │   │   ├── assemble_decision_flow()        # Build LangGraph
│   │   │   ├── generate_article_answer()       # Q&A responses
│   │   │   └── run_example()                   # Demo functionality
│   │   └── Internal Methods:
│   │       ├── _generate_article_from_document()
│   │       └── _generate_all_articles()
│   └── Class: ArticleStructure(BaseModel)
│       └── Fields: title, introduction, main_sections, conclusion, key_insights, tags
│
├── article_prompts.py               # Role definitions & prompt templates
│   ├── Enum: ArticleRole
│   │   ├── FINANCIAL_ADVISOR
│   │   ├── JOURNALIST
│   │   ├── SCIENTIFIC_RESEARCHER
│   │   ├── BUSINESS_ANALYST
│   │   ├── TECHNICAL_WRITER
│   │   ├── MARKETING_SPECIALIST
│   │   ├── POLICY_ANALYST
│   │   ├── HEALTHCARE_EXPERT
│   │   ├── LEGAL_ANALYST
│   │   ├── EDUCATOR
│   │   └── CUSTOM
│   ├── Dict: ROLE_DEFINITIONS
│   └── Functions:
│       ├── get_role_context()              # Get role description
│       ├── generate_article_prompt()       # Article generation prompt
│       ├── generate_digest_prompt()        # Digest generation prompt
│       └── generate_qa_prompt()            # Q&A prompt
│
├── run_article_generator.py         # Example scripts
│   ├── example_financial_advisor()
│   ├── example_journalist()
│   ├── example_scientific_researcher()
│   ├── example_custom_role()
│   ├── example_custom_role_shorthand()
│   ├── example_multiple_documents()
│   └── example_with_chat()
│
├── test_article_generator.py        # Test suite
│   ├── test_basic_functionality()
│   ├── test_custom_role()
│   └── test_all_roles()
│
├── README.md                         # Full documentation
├── GETTING_STARTED.md               # Quick start guide
├── QUICK_REFERENCE.md               # Quick reference
└── COMPARISON.md                    # vs News Summarizer
```

## Data Flow

```
Input Documents
      ↓
DocumentImporter (from BaseWorkFlow)
      ↓
Document Chunks
      ↓
ArticleGenerator.initialize()
      ├─→ Load documents
      ├─→ Setup retriever & tools
      ├─→ Get role context
      └─→ Generate articles for each document
            ├─→ generate_article_prompt()
            ├─→ LLM with structured output
            └─→ ArticleStructure object
      ↓
Generated Articles (List[Dict])
      ├─→ get_articles() → Return all articles
      ├─→ format_article_as_markdown() → MD string
      ├─→ save_articles_to_file() → File output
      └─→ generate_digest() → Comprehensive digest
```

## Inheritance Structure

```
BaseWorkFlow (from tools.rag.base_workflow)
      ↓
      └─→ ArticleGenerator
            ├─── Inherits:
            │     ├── _load_documents()
            │     ├── _setup_retriever_and_tools()
            │     ├── generate_query_or_respond()
            │     ├── assemble_decision_flow() [overridden]
            │     ├── invoke_chat()
            │     ├── stream_chat()
            │     └── display_state_graph()
            └─── Adds:
                  ├── Role configuration
                  ├── Article generation
                  ├── Digest creation
                  └── Markdown formatting
```

## Configuration Flow

```
User Configuration
      ↓
initialize(
  documents=[...],
  role=ArticleRole.XXX or "custom role",
  custom_role_description="...",
  article_style="formal|conversational|technical|persuasive",
  target_audience="...",
  article_length="short|medium|long",
  focus_areas="..."
)
      ↓
      ├─→ Convert role string to ArticleRole enum
      ├─→ Get role context from ROLE_DEFINITIONS
      ├─→ Store configuration
      └─→ Generate articles with config
```

## LangGraph Workflow

```
START
  ↓
query_documents (generate_query_or_respond)
  ↓
tools_condition
  ├─→ "tools" → retrieve (ToolNode with retriever)
  │              ↓
  │            answer (generate_article_answer)
  │              ↓
  │            END
  │
  └─→ END (direct response, no retrieval needed)
```

## Key Components Integration

```
ArticleGenerator
      │
      ├─→ Uses: DocumentImporter (from doc_loader)
      │         └─→ Loads various document types
      │
      ├─→ Uses: Retriever (from tools.rag)
      │         └─→ Creates searchable vector store
      │
      ├─→ Uses: LLM Model (from models)
      │         └─→ Generates content with structured output
      │
      ├─→ Uses: StateGraph (from langgraph)
      │         └─→ Builds interactive Q&A workflow
      │
      └─→ Uses: ArticleRole & Prompts
                └─→ Configures professional perspective
```

## Output Structures

### Article Dictionary
```python
{
    'title': str,
    'introduction': str,
    'main_sections': [
        {'heading': str, 'content': str},
        ...
    ],
    'conclusion': str,
    'key_insights': [str, ...],
    'tags': str,
    'metadata': {
        'source': str,
        'role': str,
        'style': str,
        'audience': str,
        'original_length': int
    }
}
```

### Markdown Format
```markdown
# {title}

**Tags:** {tags}

---

{introduction}

## {section_heading}

{section_content}

...

## Conclusion

{conclusion}

### Key Insights

- {insight_1}
- {insight_2}
...

---

*Source: {source}*
*Role: {role} | Style: {style} | Audience: {audience}*
```
