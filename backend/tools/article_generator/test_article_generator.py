"""Simple test script to verify ArticleGenerator functionality."""

from pathlib import Path
from tools.article_generator import ArticleGenerator, ArticleRole


def test_basic_functionality():
    """Test basic article generation."""
    print("\n" + "="*80)
    print("TESTING: Basic Article Generation")
    print("="*80 + "\n")
    
    try:
        generator = ArticleGenerator()
        
        # Use a document from your workspace
        test_doc = Path().resolve() / 'docs' / '2025-FedEx-Global-Economic-Impact-Report.pdf'
        
        if not test_doc.exists():
            print(f"⚠ Test document not found: {test_doc}")
            print("Please update the path or use a different document.\n")
            return
        
        print(f"📄 Analyzing: {test_doc.name}\n")
        
        generator.initialize(
            documents=[test_doc],
            role=ArticleRole.BUSINESS_ANALYST,
            article_style="formal",
            target_audience="business executives",
            article_length="short"  # Short for faster testing
        )
        
        # Test getting articles
        articles = generator.get_articles()
        print(f"✓ Generated {len(articles)} article(s)\n")
        
        # Test article structure
        if articles:
            article = articles[0]
            print("Article Structure:")
            print(f"  - Title: {article.get('title', 'N/A')[:60]}...")
            print(f"  - Sections: {len(article.get('main_sections', []))}")
            print(f"  - Key Insights: {len(article.get('key_insights', []))}")
            print(f"  - Tags: {article.get('tags', 'N/A')}")
            print()
            
            # Test markdown formatting
            md = generator.format_article_as_markdown(article)
            print(f"✓ Markdown format: {len(md)} characters\n")
        
        # Test digest generation
        digest = generator.get_digest()
        print(f"✓ Digest generated: {len(digest)} characters\n")
        
        # Test file saving
        output_path = Path('test_output_articles.md')
        generator.save_articles_to_file(output_path, format='markdown')
        
        if output_path.exists():
            print(f"✓ Articles saved to: {output_path}")
            print(f"  File size: {output_path.stat().st_size} bytes\n")
        
        print("="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()


def test_custom_role():
    """Test custom role functionality."""
    print("\n" + "="*80)
    print("TESTING: Custom Role")
    print("="*80 + "\n")
    
    try:
        generator = ArticleGenerator()
        
        custom_desc = "You are a sustainability consultant specializing in corporate environmental strategies."
        
        test_doc = Path().resolve() / 'docs' / '2025-FedEx-Global-Economic-Impact-Report.pdf'
        
        if not test_doc.exists():
            print(f"⚠ Test document not found: {test_doc}\n")
            return
        
        generator.initialize(
            documents=[test_doc],
            role=ArticleRole.CUSTOM,
            custom_role_description=custom_desc,
            article_style="persuasive",
            target_audience="corporate executives",
            article_length="short"
        )
        
        articles = generator.get_articles()
        print(f"✓ Custom role article generated\n")
        print(f"  Role: {articles[0]['metadata'].get('role')}")
        print(f"  Title: {articles[0].get('title')}\n")
        
        print("="*80)
        print("✅ CUSTOM ROLE TEST PASSED")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()


def test_all_roles():
    """Test that all predefined roles work."""
    print("\n" + "="*80)
    print("TESTING: All Predefined Roles")
    print("="*80 + "\n")
    
    roles_to_test = [
        ArticleRole.FINANCIAL_ADVISOR,
        ArticleRole.JOURNALIST,
        ArticleRole.TECHNICAL_WRITER
    ]
    
    test_doc = Path().resolve() / 'docs' / '2025-FedEx-Global-Economic-Impact-Report.pdf'
    
    if not test_doc.exists():
        print(f"⚠ Test document not found: {test_doc}\n")
        return
    
    for role in roles_to_test:
        try:
            print(f"Testing role: {role.value}...")
            generator = ArticleGenerator()
            generator.initialize(
                documents=[test_doc],
                role=role,
                article_length="short"
            )
            articles = generator.get_articles()
            print(f"  ✓ {role.value}: Generated {len(articles)} article(s)\n")
        except Exception as e:
            print(f"  ❌ {role.value} failed: {e}\n")
    
    print("="*80)
    print("✅ ROLE TESTS COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("ARTICLE GENERATOR - TEST SUITE")
    print("="*80)
    
    # Run tests
    test_basic_functionality()
    # test_custom_role()
    # test_all_roles()
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")
