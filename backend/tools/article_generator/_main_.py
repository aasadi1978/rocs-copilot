
"""Example: Financial Advisor analyzing an economic report."""

import logging
from os import getenv
from langchain_anthropic import ChatAnthropic
from tools.article_generator.article_generator import ArticleGenerator
from tools.article_generator.article_profiles import FEDEX_SME_SURVEY as article_profile
# from models import llm_basic, llm_advanced

llm = ChatAnthropic(
    model="claude-opus-4-1-20250805",
    temperature=0.2,
    # max_tokens=2048,
    timeout=None,
    max_retries=2,
    api_key=getenv("ANTHROPIC_API_KEY")
    # model_kwargs={ "http_client": HTTP_CLIENT }
)

logging.info(f"{str(article_profile['role'])} ...")
filename = article_profile['filename']
output_path = article_profile['output_path']
output_path.mkdir(parents=True, exist_ok=True)
digest_opportunities_focus=article_profile['digest_opportunities_focus']

generator = ArticleGenerator(llm_model=llm)
generator.initialize(
    documents=article_profile['documents'],
    role=article_profile['role'],
    article_style=article_profile['article_style'],
    target_audience=article_profile['target_audience'],
    article_length=article_profile['article_length'],
    focus_areas=article_profile['focus_areas'],
    consolidate_docs=article_profile['consolidate_docs']
)

# Get and save articles
articles = generator.get_articles()
logging.info(f"✓ Generated {len(articles)} article(s)\n")

# Save as Markdown
generator.save_articles_to_file(f'{output_path}/{filename}.md', format='markdown')
logging.info(f"✓ Saved to {output_path}/{filename}.md\n")

# Save as DOCX for LinkedIn
generator.save_articles_to_file(f'{output_path}/{filename}.docx', format='docx')
logging.info(f"✓ Saved to {output_path}/{filename}.docx (ready for LinkedIn)\n")

# Generate digest

logging.info(f"Generating digest focused on {digest_opportunities_focus} ...")
digest = generator.get_digest(digest_focus=digest_opportunities_focus)

# Save digest
with open(f'{output_path}/digest_{filename}.md', 'w', encoding='utf-8') as f:
    f.write(digest)
logging.info(f"✓ Digest saved to {output_path}/digest_{filename}.md")

# Save as DOCX for LinkedIn
generator.save_articles_to_file(f'{output_path}/digest_{filename}.docx', format='docx')
logging.info(f"✓ Saved to {output_path}/digest_{filename}.docx (ready for LinkedIn)\n")

def interactive_chat():
    """Example: Using the integrated interactive chat interface for Q&A with history."""
    print("\n" + "="*80)
    print("EXAMPLE 7: Interactive Q&A with Article Generator + History")
    print("="*80 + "\n")
    print("Starting interactive chat mode with article generator...")
    print("This uses the integrated api.interactive_chat module with full history support.\n")
    
    # Use the integrated interactive chat system
    from api.interactive_chat import start_interactive_chat
    
    # Start in article mode
    start_interactive_chat(mode="article")
