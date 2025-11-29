
"""Example: Financial Advisor analyzing an economic report."""

import logging
from os import getenv
from pathlib import Path
from langchain_anthropic import ChatAnthropic
from tools.article_generator.article_generator import ArticleGenerator
from tools.article_generator.article_prompts import ArticleRole
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

logging.info("McKinsey consultant - Economic Report Analysis")
docs_path = Path().resolve() / 'docs'

generator = ArticleGenerator(llm_model=llm)
generator.initialize(
    documents=[
        docs_path / 'the-state-of-ai-in-2025-agents-innovation-and-transformation.pdf',
        docs_path / '2025-FedEx-Global-Economic-Impact-Report.pdf',
        docs_path / 'en-fr_pdf_na_CDG_impact.pdf'
    ],

    role=ArticleRole.MCKINSEY_CONSULTANT,
    article_style="formal",
    target_audience="FedEx Express leadership team",
    article_length="medium",
    focus_areas="FedEx growth and profitability in Europe, the impact of AI and automation on logistics, recommendations for strategic investments",
    consolidate_docs=True
)

# Get and save articles
articles = generator.get_articles()
logging.info(f"✓ Generated {len(articles)} article(s)\n")

# Save as Markdown
generator.save_articles_to_file('fedex-global-economic-report-summary.md', format='markdown')
logging.info("✓ Saved to fedex-global-economic-report-summary.md\n")

# Save as DOCX for LinkedIn
generator.save_articles_to_file('fedex-global-economic-report-summary.docx', format='docx')
logging.info("✓ Saved to fedex-global-economic-report-summary.docx (ready for LinkedIn)\n")

# Generate digest
_opportunities_focus="Growth opportunities and strategic recommendations for profitability of FedEx Express in Europe"
logging.info(f"Generating digest focused on {_opportunities_focus} ...")
digest = generator.get_digest(digest_focus=_opportunities_focus)

# Save digest
with open('digest_fedex-global-economic-report-summary.md', 'w', encoding='utf-8') as f:
    f.write(digest)
logging.info("✓ Digest saved to digest_fedex-global-economic-report-summary.md")

# Save as DOCX for LinkedIn
generator.save_articles_to_file('digest_fedex-global-economic-report-summary.docx', format='docx')
logging.info("✓ Saved to digest_fedex-global-economic-report-summary.docx (ready for LinkedIn)\n")