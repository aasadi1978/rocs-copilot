"""Summarize news articles using LLM."""

import logging
from typing import List, Dict
from langchain_core.documents import Document
from langchain_anthropic import ChatAnthropic as AIChatClass
from models import llm_basic


class NewsSummarizer:
    """Summarizes news articles using an LLM."""
    
    def __init__(self, llm: AIChatClass = None):
        """
        Initialize the news summarizer.
        
        Args:
            llm: Optional LLM model. Defaults to llm_basic from models module
        """
        self.llm = llm or llm_basic
    
    def summarize_article(self, article: Document, summary_length: str = "medium") -> Dict[str, str]:
        """
        Summarize a single news article.
        
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
        
        prompt = f"""You are a professional news analyst. Analyze the following news article and provide:

        1. A summary ({instruction})
        2. 3-5 key points (bullet points)
        3. Main topics/categories (e.g., technology, politics, business, etc.)

        Article Title: {article.metadata.get('title', 'Untitled')}
        Article URL: {article.metadata.get('source', '')}

        Article Content:
        {article.page_content}

        Respond in the following format:
        SUMMARY:
        [Your summary here]

        KEY POINTS:
        - [Point 1]
        - [Point 2]
        - [Point 3]
        ...

        TOPICS:
        [Comma-separated topics]
        """
        
        try:
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            content = response.content
            
            # Parse the response
            summary = ""
            key_points = []
            topics = ""
            
            sections = content.split('\n\n')
            current_section = None
            
            for section in sections:
                section = section.strip()
                if section.startswith('SUMMARY:'):
                    current_section = 'summary'
                    summary = section.replace('SUMMARY:', '').strip()
                elif section.startswith('KEY POINTS:'):
                    current_section = 'key_points'
                elif section.startswith('TOPICS:'):
                    current_section = 'topics'
                    topics = section.replace('TOPICS:', '').strip()
                elif current_section == 'summary' and not summary:
                    summary = section
                elif current_section == 'key_points':
                    # Extract bullet points
                    lines = section.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('-') or line.startswith('•'):
                            key_points.append(line.lstrip('-').lstrip('•').strip())
                elif current_section == 'topics' and not topics:
                    topics = section
            
            return {
                "title": article.metadata.get('title', 'Untitled'),
                "url": article.metadata.get('source', ''),
                "publish_date": article.metadata.get('publish_date', ''),
                "summary": summary,
                "key_points": key_points,
                "topics": topics,
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
    
    def summarize_multiple_articles(self, articles: List[Document], 
                                    summary_length: str = "medium") -> List[Dict[str, str]]:
        """
        Summarize multiple news articles.
        
        Args:
            articles: List of Document objects containing news articles
            summary_length: Length of summaries
            
        Returns:
            List of dictionaries with summaries and metadata
        """
        summaries = []
        
        for i, article in enumerate(articles, 1):
            logging.info(f"Summarizing article {i}/{len(articles)}: {article.metadata.get('title', 'Untitled')[:50]}...")
            summary = self.summarize_article(article, summary_length)
            summaries.append(summary)
        
        return summaries
    
    def generate_digest(self, summaries: List[Dict[str, str]]) -> str:
        """
        Generate an overall news digest from multiple article summaries.
        
        Args:
            summaries: List of article summary dictionaries
            
        Returns:
            A comprehensive news digest
        """
        if not summaries:
            return "No articles to summarize."
        
        # Prepare the context
        articles_text = []
        for i, summary in enumerate(summaries, 1):
            articles_text.append(f"""
Article {i}: {summary['title']}
URL: {summary['url']}
Topics: {summary['topics']}
Summary: {summary['summary']}
Key Points:
{chr(10).join(['- ' + point for point in summary['key_points']])}
""")
        
        combined_text = '\n---\n'.join(articles_text)
        
        prompt = f"""You are a news editor creating a daily news digest. Based on the following article summaries, 
create a comprehensive news digest that:
1. Highlights the most important stories
2. Groups related stories by topic
3. Provides context and connections between stories
4. Is well-organized and easy to read

Here are the article summaries:

{combined_text}

Create a professional news digest with clear sections and compelling presentation.
"""
        
        try:
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            return response.content
        except Exception as e:
            logging.error(f"Error generating digest: {e}")
            return f"Error generating digest: {str(e)}"
