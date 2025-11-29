"""Example usage of News Tracker that leverages existing RAG infrastructure.

This shows how to use the news tracker without duplicating any RAG functionality.
"""

from tools.rag.workflow import RAG_WORKFLOW_INSTANCE


def init_news_tracker():
    """Initialize the News Tracker workflow using existing RAG components."""
    
    # Configure your news sources
    news_list = [
        "https://www.ad.nl/rijswijk/",
        "https://www.ad.nl/",
        "https://www.ad.nl/net-binnen-rijswijk/",
        "https://www.ad.nl/nieuws/"
    ]
    
    print("Initializing News Tracker (using existing RAG infrastructure)...")
    
    # Initialize with news URLs
    # This uses DocLoader and load_url.py from your RAG package
    RAG_WORKFLOW_INSTANCE.initialize(
        data_sources=news_list,
        description="Latest news articles from selected Dutch news sources.",
        name="News Tracker Agent"
    )
    
    RAG_WORKFLOW_INSTANCE.build_graph()


if __name__ == "__main__":
    """
    Run this file directly to test the News Tracker Agent.
    Usage: python -m backend.tools.news_tracker.init_news_tracker
    """
    
    # Initialize the news tracker
    tracker = init_news_tracker()
    
    # Example 1: Run the built-in example
    tracker.run_example()
    
    # Example 2: Get just the digest
    print("\n" + "="*80)
    print("NEWS DIGEST")
    print("="*80 + "\n")
    digest = tracker.get_digest()
    print(digest)
    
    # Example 3: Ask specific questions
    print("\n" + "="*80)
    print("INTERACTIVE QUERIES")
    print("="*80 + "\n")
    
    question = "What are the main topics covered in these articles?"
    print(f"Q: {question}")
    print(f"A: {tracker.query_news(question)}")
