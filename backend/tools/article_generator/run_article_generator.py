"""Example script demonstrating the ArticleGenerator with different professional roles.

This script shows how to:
1. Use predefined professional roles
2. Define custom roles
3. Generate articles from various document types
4. Create comprehensive digests
5. Save articles in different formats
"""

from pathlib import Path
from tools.article_generator import ArticleGenerator, ArticleRole


def example_financial_advisor():
    """Example: Financial Advisor analyzing an economic report."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Financial Advisor - Economic Report Analysis")
    print("="*80 + "\n")
    
    generator = ArticleGenerator()
    generator.initialize(
        documents=[
            Path().resolve() / 'docs' / '2025-FedEx-Global-Economic-Impact-Report.pdf'
        ],
        role=ArticleRole.FINANCIAL_ADVISOR,
        article_style="formal",
        target_audience="investment professionals and portfolio managers",
        article_length="medium",
        focus_areas="investment implications, market trends, economic indicators"
    )
    
    # Get and save articles
    articles = generator.get_articles()
    print(f"✓ Generated {len(articles)} article(s)\n")
    
    # Save as Markdown
    generator.save_articles_to_file('output_financial_analysis.md', format='markdown')
    print("✓ Saved to output_financial_analysis.md\n")
    
    # Generate digest
    digest = generator.get_digest(digest_focus="investment opportunities and risk factors")
    print("DIGEST:\n")
    print(digest)
    
    # Save digest
    with open('digest_financial.md', 'w', encoding='utf-8') as f:
        f.write(digest)
    print("\n✓ Digest saved to digest_financial.md")


def example_journalist():
    """Example: Journalist writing news articles."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Journalist - News Article Writing")
    print("="*80 + "\n")
    
    generator = ArticleGenerator()
    generator.initialize(
        documents=[
            'https://newsroom.fedex.com/newsroom/global-english/fedex-dataworks-and-servicenow-unite-ai-data-and-workflows-to-power-supply-chains-of-the-future'
        ],
        role=ArticleRole.JOURNALIST,
        article_style="conversational",
        target_audience="general public interested in technology and business",
        article_length="medium"
    )
    
    articles = generator.get_articles()
    print(f"✓ Generated {len(articles)} article(s)\n")
    
    # Display first article
    if articles:
        print("FIRST ARTICLE:\n")
        print(generator.format_article_as_markdown(articles[0]))


def example_scientific_researcher():
    """Example: Scientific Researcher analyzing research papers."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Scientific Researcher - Research Analysis")
    print("="*80 + "\n")
    
    generator = ArticleGenerator()
    generator.initialize(
        documents=[
            Path().resolve() / 'docs'  # Analyze all documents in docs folder
        ],
        role=ArticleRole.SCIENTIFIC_RESEARCHER,
        article_style="technical",
        target_audience="academic researchers and graduate students",
        article_length="long",
        focus_areas="methodology, findings, implications for future research"
    )
    
    articles = generator.get_articles()
    print(f"✓ Generated {len(articles)} article(s)\n")
    
    # Save as JSON for programmatic access
    generator.save_articles_to_file('output_research_analysis.json', format='json')
    print("✓ Saved to output_research_analysis.json")


def example_custom_role():
    """Example: Custom role - Supply Chain Expert."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Custom Role - Supply Chain Expert")
    print("="*80 + "\n")
    
    custom_role_desc = """You are a senior supply chain strategist with 20+ years of experience 
in logistics optimization, global trade, and supply chain resilience. You provide strategic 
insights that help companies build more efficient, sustainable, and adaptive supply chains."""
    
    generator = ArticleGenerator()
    generator.initialize(
        documents=[
            Path().resolve() / 'docs' / '2025-FedEx-Global-Economic-Impact-Report.pdf'
        ],
        role=ArticleRole.CUSTOM,  # Using CUSTOM role
        custom_role_description=custom_role_desc,
        article_style="persuasive",
        target_audience="supply chain executives and operations leaders",
        article_length="medium",
        focus_areas="supply chain optimization, resilience strategies, cost reduction"
    )
    
    articles = generator.get_articles()
    print(f"✓ Generated {len(articles)} article(s)\n")
    
    if articles:
        print("GENERATED ARTICLE:\n")
        print(generator.format_article_as_markdown(articles[0]))


def example_custom_role_shorthand():
    """Example: Custom role using string shorthand."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Custom Role Shorthand - Data Scientist")
    print("="*80 + "\n")
    
    generator = ArticleGenerator()
    generator.initialize(
        documents=[
            'https://www.deeplearning.ai/the-batch/issue-329/'
        ],
        role="data scientist",  # Pass role as string - will be converted to custom
        article_style="technical",
        target_audience="machine learning practitioners",
        article_length="short"
    )
    
    articles = generator.get_articles()
    print(f"✓ Generated {len(articles)} article(s)\n")
    
    digest = generator.get_digest()
    print("DIGEST:\n")
    print(digest)


def example_multiple_documents():
    """Example: Analyzing multiple documents with Business Analyst role."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Business Analyst - Multiple Document Analysis")
    print("="*80 + "\n")
    
    generator = ArticleGenerator()
    generator.initialize(
        documents=[
            'https://www.forbes.com/councils/forbesbusinesscouncil/2025/11/26/how-europe-can-prepare-young-professionals-for-the-ai-economy/',
            'https://cio.economictimes.indiatimes.com/news/artificial-intelligence/from-data-to-intelligence-the-rise-of-smarter-predictive-supply-chains/125324044',
            Path().resolve() / 'docs' / '2025-FedEx-Global-Economic-Impact-Report.pdf'
        ],
        role=ArticleRole.BUSINESS_ANALYST,
        article_style="formal",
        target_audience="C-suite executives and business strategists",
        article_length="medium",
        focus_areas="competitive advantages, market opportunities, strategic recommendations"
    )
    
    articles = generator.get_articles()
    print(f"✓ Generated {len(articles)} article(s)\n")
    
    # Generate comprehensive digest
    digest = generator.get_digest(digest_focus="strategic business opportunities and competitive trends")
    
    # Save everything
    generator.save_articles_to_file('output_business_analysis.md')
    with open('digest_business.md', 'w', encoding='utf-8') as f:
        f.write(digest)
    
    print("✓ Saved articles to output_business_analysis.md")
    print("✓ Saved digest to digest_business.md")


def example_with_chat():
    """Example: Using the chat interface for Q&A."""
    print("\n" + "="*80)
    print("EXAMPLE 7: Interactive Q&A with Technical Writer Role")
    print("="*80 + "\n")
    
    generator = ArticleGenerator()
    generator.initialize(
        documents=[
            Path().resolve() / 'docs' / '2025-FedEx-Global-Economic-Impact-Report.pdf'
        ],
        role=ArticleRole.TECHNICAL_WRITER,
        article_style="conversational",
        target_audience="technical professionals",
        article_length="medium"
    )
    
    # Build the graph for interactive queries
    generator.display_state_graph(graph_name="article_generator_workflow")
    
    # Ask questions
    print("ASKING QUESTIONS:\n")
    
    questions = [
        "What are the key technical insights from this document?",
        "How would you explain the main concepts to a non-technical audience?",
        "What are the practical applications mentioned?"
    ]
    
    for question in questions:
        print(f"Q: {question}")
        result = generator.invoke_chat([{"role": "user", "content": question}])
        print(f"A: {result['messages'][-1].content}\n")


def main():
    """Run all examples or specific ones."""
    
    print("\n" + "="*80)
    print("ARTICLE GENERATOR EXAMPLES")
    print("Demonstrating different professional roles and use cases")
    print("="*80)
    
    # Uncomment the examples you want to run:
    
    # Example 1: Financial Advisor
    # example_financial_advisor()
    
    # Example 2: Journalist
    # example_journalist()
    
    # Example 3: Scientific Researcher
    # example_scientific_researcher()
    
    # Example 4: Custom Role (Supply Chain Expert)
    example_custom_role()
    
    # Example 5: Custom Role Shorthand
    # example_custom_role_shorthand()
    
    # Example 6: Multiple Documents
    # example_multiple_documents()
    
    # Example 7: Interactive Chat
    # example_with_chat()
    
    print("\n" + "="*80)
    print("EXAMPLES COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
