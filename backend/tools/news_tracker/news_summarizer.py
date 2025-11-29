"""News Summarizer Workflow - RAG-based news article summarization and analysis."""

import logging
from typing import List, Dict, Union, Literal
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from tools.news_tracker.news_prompts import generate_answer_prompt, get_digest_prompt, get_summarizer_prompt
from tools.rag import AIChatClass
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from tools.rag.base_workflow import BaseWorkFlow, RAGState


class ArticleSummary(BaseModel):
    """Structured output for article summary."""
    
    summary: str = Field(
        description="The main summary of the article based on the specified length"
    )
    key_points: List[str] = Field(
        description="3-5 key points from the article as bullet points",
        min_items=3,
        max_items=5
    )
    topics: str = Field(
        description="Comma-separated main topics/categories (e.g., technology, politics, business)"
    )


class NewsSummarizer(BaseWorkFlow):
    """Summarizes and analyzes news articles using RAG workflow.
    
    Extends BaseWorkflow to provide:
    - News article loading and chunking
    - Article summarization with key points extraction
    - News digest generation
    - Interactive Q&A about news content
    """
    
    def __init__(self, llm_model: AIChatClass = None):
        """
        Initialize the news summarizer workflow.
        
        Args:
            llm_model: Optional LLM model. Defaults to llm_basic from models module
        """
        super().__init__(llm_model)
        self._summaries: List[Dict] = []
        self._summary_length: str = "medium"
    
    def initialize(self,
                   news_urls: Union[List[str], List[Path]],
                   summary_length: str = "medium",
                   chunk_size: int = 2000,
                   chunk_overlap: int = 200,
                   name: str = "NewsRetriever",
                   description: str = "Retrieves relevant news articles based on queries"):
        """
        Initialize the news summarizer with news URLs.
        
        Args:
            news_urls: List of news article URLs to load and summarize
            summary_length: Length of summaries - "short", "medium", or "detailed"
            chunk_size: Size of document chunks (larger for news articles)
            chunk_overlap: Overlap between chunks
            name: Name for the retriever
            description: Description of the retriever
        """
        try:
            self._summary_length = summary_length
            
            # Load news articles using base class method
            self._load_documents(
                data_sources=news_urls,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                use_cache=True
            )
            
            # Setup retriever and tools
            self._setup_retriever_and_tools(
                name=name,
                description=description
            )
            
            # Generate summaries for all loaded articles
            logging.info("Generating article summaries...")
            self._summaries = self._summarize_all_articles()
            
            logging.info(f"News Summarizer initialized with {len(self._summaries)} article summaries.")
            
        except Exception as e:
            logging.error(f"Error initializing news summarizer: {e}")
            raise
    
    def __summarize_article(self, article: Document, 
                          summary_length: Literal["short", "medium", "detailed"] = "medium") -> Dict[str, str]:
        """
        Summarize a single news article using structured output.
        
        Args:
            article: Document containing the news article
            summary_length: Length of summary - "short" (2-3 sentences), "medium" (1 paragraph), 
                          or "detailed" (multiple paragraphs)
            
        Returns:
            Dictionary with summary, key_points, and metadata
        """
        
        length_instructions = {
            "short": "Provide a concise 2-3 sentence summary.",
            "medium": "Provide a one-paragraph summary (4-6 sentences).",
            "detailed": "Provide a comprehensive summary with multiple paragraphs covering all key points."
        }
        
        instruction = length_instructions.get(summary_length, length_instructions["medium"])
        prompt = get_summarizer_prompt(instruction, article)

        try:
            # Use structured output to ensure consistent format
            structured_llm = self._llm_model.with_structured_output(ArticleSummary)
            response: ArticleSummary = structured_llm.invoke([{"role": "user", "content": prompt}])
            
            return {
                "title": article.metadata.get('title', 'Untitled'),
                "url": article.metadata.get('source', ''),
                "publish_date": article.metadata.get('publish_date', ''),
                "summary": response.summary,
                "key_points": response.key_points,
                "topics": response.topics,
                "original_length": len(article.page_content)
            }
            
        except Exception as e:
            logging.error(f"Error summarizing article: {e}")
            return {
                "title": article.metadata.get('title', 'Untitled'),
                "url": article.metadata.get('source', ''),
                "summary": f"Error generating summary: {str(e)}",
                "key_points": [],
                "topics": "",
                "original_length": 0
            }
    
    def _summarize_all_articles(self) -> List[Dict[str, str]]:
        """Summarize all loaded articles.
        
        Returns:
            List of article summary dictionaries
        """
        summaries = []

        if not self._documents:
            logging.warning("No documents available to summarize.")
            return summaries
        
        # Group documents by source URL to avoid duplicate summaries
        articles_by_url = {}
        for doc in self._documents:
            url = doc.metadata.get('source', '')
            if url and url not in articles_by_url:
                articles_by_url[url] = doc
        
        for i, (url, article) in enumerate(articles_by_url.items(), 1):
            logging.info(f"Summarizing article {i}/{len(articles_by_url)}: {article.metadata.get('title', 'Untitled')[:50]}...")
            summary = self.__summarize_article(article, self._summary_length)
            summaries.append(summary)
        
        return summaries
    
    def generate_digest(self, summaries: List[Dict[str, str]] = None) -> str:
        """
        Generate an overall news digest from multiple article summaries.
        
        Args:
            summaries: Optional list of article summary dictionaries. If not provided, uses self._summaries
            
        Returns:
            A comprehensive news digest
        """

        if not summaries:
            return "No articles to summarize."
        
        # Prepare the context
        articles_text = self.__process_article_summaries(summaries)
        
        combined_text = '\n---\n'.join(articles_text)
        
        try:
            response = self._llm_model.invoke([{"role": "user", "content": get_digest_prompt(combined_text)}])
            return response.content
        
        except Exception as e:
            logging.error(f"Error generating digest: {e}")
            return f"Error generating digest: {str(e)}"

    def __process_article_summaries(self, summaries):
        articles_text = []
        for i, summary in enumerate(summaries, 1):
            try:
                articles_text.append(f"""Article {i}: {summary['title']}
URL: {summary['url']}
Topics: {summary['topics']}
Summary: {summary['summary']}
Key Points: {chr(10).join(['- ' + point for point in summary['key_points']])}""")
            except Exception as e:
                logging.error(f"Error preparing article {i} for digest: {e}")
                continue

        return articles_text
    
    def create_social_media_post(self, 
                                  platform: Literal["twitter", "linkedin", "facebook", "instagram"] = "twitter",
                                  summary_index: int = None,
                                  include_hashtags: bool = True,
                                  max_length: int = 500,
                                  tone: Literal["professional", "casual", "engaging"] = "engaging") -> str:
        """
        Generate a social media post from an article summary.
        
        Args:
            platform: Social media platform - "twitter", "linkedin", "facebook", or "instagram"
            summary_index: Index of the article summary to use (0-based). If None, uses the first article
            include_hashtags: Whether to include hashtags in the post
            tone: Tone of the post - "professional", "casual", or "engaging"
            
        Returns:
            Formatted social media post string
        """
        if not self._summaries:
            raise ValueError("No summaries available. Call initialize() first.")
        
        # Get the article summary
        if summary_index is None:
            summary_index = 0
        
        if summary_index >= len(self._summaries):
            raise ValueError(f"Invalid summary_index {summary_index}. Only {len(self._summaries)} summaries available.")
        
        article = self._summaries[summary_index]
        
        # Platform-specific character limits and formatting
        platform_specs = {
            "twitter": {"char_limit": 280, "emoji_style": "minimal", "format": "concise"},
            "linkedin": {"char_limit": 3000, "emoji_style": "professional", "format": "detailed"},
            "facebook": {"char_limit": 63206, "emoji_style": "friendly", "format": "conversational"},
            "instagram": {"char_limit": 2200, "emoji_style": "abundant", "format": "visual"}
        }
        
        spec = platform_specs.get(platform, platform_specs["twitter"])
        
        # Build the prompt
        hashtag_instruction = "Include 3-5 relevant hashtags at the end." if include_hashtags else "Do not include hashtags."
        
        prompt = f"""Create an engaging social media post for {platform.upper()} based on this news article:

Title: {article['title']}
Summary: {article['summary']}
Key Points: {', '.join(article['key_points'])}
Topics: {article['topics']}

Requirements:
- maximum length: {max_length} characters
- Platform: {platform}
- Character limit: {spec['char_limit']} characters (stay well under this)
- Tone: {tone}
- Style: {spec['format']}
- {hashtag_instruction}
- Include a call-to-action or engaging question if appropriate
- Use emojis appropriately for {spec['emoji_style']} style
- Make it attention-grabbing and shareable

Generate ONLY the social media post text, nothing else."""

        try:
            response = self._llm_model.invoke([{"role": "user", "content": prompt}])
            post = response.content.strip()
            
            # Add source URL if available
            if article.get('url') and platform in ["linkedin", "facebook"]:
                post += f"\n\n🔗 Read more: {article['url']}"
            
            return post
            
        except Exception as e:
            logging.error(f"Error generating social media post: {e}")
            return f"Error generating post: {str(e)}"
    
    def get_summaries(self) -> List[Dict[str, str]]:
        """Get all article summaries.
        
        Returns:
            List of article summary dictionaries
        """
        if not self._summaries:
            raise ValueError("No summaries available. Call initialize() first.")
        
        return self._summaries
    
    def get_digest(self) -> str:
        """Generate and return a comprehensive news digest.
        
        Returns:
            Formatted news digest string
        """
        if not self._summaries:
            raise ValueError("No summaries available. Call initialize() first.")
        
        return self.generate_digest(self._summaries)
    
    def assemble_decision_flow(self):
        """Assemble news-specific decision flow for the workflow graph. This graph is used to build a LangGraph workflow for a chat-based news Q&A system.
        Override to create a simpler flow focused on news queries without
        document grading and question rewriting (news articles are pre-summarized).
        """
        retriever_tool = self._get_retriever_tool()
        if not retriever_tool:
            raise ValueError("Failed to get retriever tool. Check initialization logs for details.")

        decision_flow = StateGraph(RAGState)

        # Simpler flow for news: query -> retrieve -> answer
        decision_flow.add_node("query_news", self.generate_query_or_respond)
        decision_flow.add_node("retrieve", ToolNode([retriever_tool]))
        decision_flow.add_node("answer", self.generate_news_answer)

        decision_flow.add_edge(START, "query_news")
        
        # Use tools_condition to decide if we need retrieval
        decision_flow.add_conditional_edges(
            "query_news",
            tools_condition,
            {
                "tools": "retrieve",
                END: END,
            },
        )
        
        decision_flow.add_edge("retrieve", "answer")
        decision_flow.add_edge("answer", END)

        return decision_flow
    
    def generate_news_answer(self, state: RAGState):
        """Generate answer for news queries using retrieved context and summaries.
        
        Args:
            state: Current RAG state with messages and metadata
            
        Returns:
            Updated state with news-focused answer
        """

        question = state["messages"][0].content
        context = state["messages"][-1].content
        
        # Include summaries in the context
        summaries_text = "\n".join([
            f"- {s['title']}: {s['summary']}" 
            for s in self._summaries[:5]  # Top 5 summaries
        ])
        
        prompt = generate_answer_prompt(
            question=question, 
            context=context,
            summaries=summaries_text
        )
        response = self._llm_model.invoke([{"role": "user", "content": prompt}])
        return {"messages": [response]}
    
    def run_example(self):
        """Example showing how to use the news summarizer."""
        if not self._summaries:
            raise ValueError("No summaries available. Call initialize() first.")
        
        print("\n" + "="*80)
        print("NEWS SUMMARIZER - EXAMPLE RUN")
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
        
        # Example query
        if self._workflow_graph:
            print("\n" + "="*80)
            print("EXAMPLE QUERY")
            print("="*80 + "\n")
            
            result = self.invoke_chat([{"role": "user", "content": "What are the main topics in these news articles?"}])
            print("Answer:", result["messages"][-1].content)


# Example usage:
# summarizer = NewsSummarizer()
# summarizer.initialize(news_urls=['https://...', 'https://...'])
# digest = summarizer.get_digest()
# summarizer.build_graph()
# summarizer.run_example()
