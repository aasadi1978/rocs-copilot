"""News Tracker Workflow - Leverages existing RAG infrastructure for news summarization.

This workflow reuses the existing RAG components (DocLoader, load_url, etc.) 
instead of duplicating functionality.
"""

import logging
from typing import List, Dict
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document
from dotenv import load_dotenv

from models import llm_basic
from doc_loader.doc_importer import DocumentImporter
from tools.news_tracker.news_summarizer import NewsSummarizer

load_dotenv()


class NewsWorkflow:
    """
    News tracking workflow that leverages existing RAG infrastructure.
    
    - Uses DocLoader from RAG package to load news URLs
    - Adds news-specific summarization on top
    - Generates comprehensive news digests
    - Provides interactive chat interface for news queries
    """
    
    _instance = None
    _llm_model: ChatAnthropic = None
    _doc_loader: DocumentImporter = None
    _news_summarizer: NewsSummarizer = None
    _articles: List[Document] = None
    _summaries: List[Dict] = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(NewsWorkflow, cls).__new__(cls)
            cls._instance._llm_model = llm_basic
            cls._instance._doc_loader = None
            cls._instance._news_summarizer = None
            cls._instance._articles = None
            cls._instance._summaries = None
        return cls._instance
    
    def __init__(self):
        pass
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the NewsWorkflow."""
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self, news_urls: List[str], summary_length: str = "medium"):
        """
        Initialize the news workflow with a list of news URLs.
        Uses existing RAG DocLoader to load articles.
        
        Args:
            news_urls: List of news article URLs to track and summarize
            summary_length: Length of summaries - "short", "medium", or "detailed"
        """
        try:
            if not news_urls:
                raise ValueError("news_urls cannot be None or empty.")
            
            logging.info(f"Initializing News Tracker with {len(news_urls)} URLs...")
            
            # Use existing DocLoader from RAG package
            self._doc_loader = DocumentImporter(
                data_sources=news_urls,
                chunk_size=2000,  # Larger chunks for news articles
                chunk_overlap=200,
                use_cache=True
            )
            
            # Load all news articles
            self._doc_loader.load_docs()
            self._articles = self._doc_loader.documents
            
            if not self._articles:
                raise ValueError("No articles were loaded. Please check your URLs and ensure they are accessible.")
            
            # Initialize summarizer
            self._news_summarizer = NewsSummarizer(llm=self._llm_model)
            
            # Generate summaries
            logging.info("Generating article summaries...")
            self._summaries = self._news_summarizer.summarize_multiple_articles(
                self._articles, 
                summary_length=summary_length
            )
            
            logging.info(f"News Tracker initialized successfully with {len(self._summaries)} article summaries.")
            
        except Exception as e:
            logging.error(f"Error initializing news workflow: {e}")
            raise
    
    def get_summaries(self) -> List[Dict[str, str]]:
        """Get all article summaries."""
        if not self._summaries:
            raise ValueError("No summaries available. Call initialize() first.")
        return self._summaries
    
    def get_digest(self) -> str:
        """Generate and return a comprehensive news digest."""
        if not self._summaries:
            raise ValueError("No summaries available. Call initialize() first.")
        return self._news_summarizer.generate_digest(self._summaries)
    
    def query_news(self, query: str) -> str:
        """
        Answer a specific query about the loaded news articles.
        
        Args:
            query: User's question about the news
            
        Returns:
            AI-generated answer based on the news content
        """
        if not self._summaries:
            raise ValueError("No summaries available. Call initialize() first.")
        
        # Prepare context from summaries
        context = []
        for summary in self._summaries:
            context.append(f"""
Title: {summary['title']}
URL: {summary['url']}
Topics: {summary['topics']}
Summary: {summary['summary']}
Key Points: {', '.join(summary['key_points'])}
""")
        
        combined_context = '\n---\n'.join(context)
        
        prompt = f"""You are a news analyst assistant. Answer the following question based on the news articles provided.

Question: {query}

News Articles Context:
{combined_context}

Provide a clear, concise answer based on the information from the news articles. If the information is not available in the articles, say so.
"""
        
        try:
            response = self._llm_model.invoke([{"role": "user", "content": prompt}])
            return response.content
        except Exception as e:
            logging.error(f"Error querying news: {e}")
            return f"Error processing query: {str(e)}"
    
    def run_example(self):
        """Example showing how to use the news tracker."""
        if not self._summaries:
            raise ValueError("No summaries available. Call initialize() first.")
        
        print("\n" + "="*80)
        print("NEWS TRACKER - EXAMPLE RUN")
        print("="*80 + "\n")
        
        # Show digest
        print("📰 GENERATING NEWS DIGEST...\n")
        digest = self.get_digest()
        print(digest)
        print("\n" + "="*80 + "\n")
        
        # Show individual summaries
        print("📋 INDIVIDUAL ARTICLE SUMMARIES:\n")
        for i, summary in enumerate(self._summaries, 1):
            print(f"\n{i}. {summary['title']}")
            print(f"   URL: {summary['url']}")
            print(f"   Topics: {summary['topics']}")
            print(f"   Summary: {summary['summary']}")
            print(f"   Key Points:")
            for point in summary['key_points']:
                print(f"   - {point}")
            print()


# Create singleton instance
NEWS_TRACKER_INSTANCE = NewsWorkflow.get_instance()
