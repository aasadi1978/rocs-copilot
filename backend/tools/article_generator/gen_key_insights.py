import logging
from os import getenv
from pathlib import Path
from typing import Any, Dict, List, Literal, Union
from langchain_anthropic import ChatAnthropic
from tools.article_generator.article_prompts import ArticleRole, get_role_context

advanced_llm_name = "claude-opus-4-1-20250805"
basic_llm_name = "claude-haiku-4-5-20251001"

llm_model = ChatAnthropic(
    model=basic_llm_name,
    temperature=0.2,
    # max_tokens=2048,
    timeout=None,
    max_retries=2,
    api_key=getenv("ANTHROPIC_API_KEY")
)


class ArticleInsightsGenerator:

    def __init__(self, llm: ChatAnthropic | None = None):
        self._llm_model = llm or llm_model
        

    def get_key_insights(
            self,
            articles: List[Dict[str, Any]],
            role: ArticleRole = ArticleRole.MCKINSEY_CONSULTANT,
            summary_length: int = 150,
            max_takeaways: int = 7,
            target_audience: str = "senior management",
            format: Literal["email", "plain"] = "plain"
        ) -> str:
            """Generate executive summary email for senior management.
            
            Creates a concise email with an executive summary and key takeaways
            from loaded documents or generated articles, suitable for senior management briefings.
            Works directly with documents if articles haven't been generated yet.
            
            Args:
                summary_length: Maximum length of executive summary in words (default: 100)
                max_takeaways: Maximum number of key takeaways to include (default: 5)
                format: Output format - "email" for email template, "plain" for plain text
                
            Returns:
                Formatted email content or plain text summary
                
            Example:
                >>> summary_email = generator.get_key_insights(summary_length=75, max_takeaways=3)
                >>> print(summary_email)
            """
            # Check if we have articles or documents to work with
            if not articles:
                raise ValueError("No articles available. Provide articles as input.")
            
            # Work with articles if available, otherwise use documents directly
            if articles:
                # Collect all key insights from articles
                all_insights = []
                article_titles = []
                
                for article in articles:
                    article_titles.append(article.get('title', 'Untitled'))
                    insights = article.get('key_insights', [])
                    all_insights.extend(insights)
                
                # Prepare context for LLM from articles
                articles_context = "\n\n".join([
                    f"Article: {article['title']}\n"
                    f"Introduction: {article['introduction'][:200]}...\n"
                    f"Key Insights: {chr(10).join(['- ' + insight for insight in article['key_insights']])}"
                    for article in articles
                ])
                
                source_count = len(articles)
                source_list = [article["metadata"].get("source", "N/A")[:100] for article in articles[:3]]
                

            role_context = get_role_context(role)
            # Create prompt for executive summary
            prompt = f"""Based on the following articles, create a concise executive summary for senior management.

    {articles_context}

    Requirements:
    1. Executive Summary: Write a clear, concise summary in approximately {summary_length} words
    2. Key Takeaways: Extract the {max_takeaways} most important takeaways
    3. Tone: Professional, action-oriented, suitable for C-level executives
    4. Focus: Strategic insights and business implications

    Role Context: {role_context}

    Format the output as:
    EXECUTIVE SUMMARY
    [Your {summary_length}-word summary here]

    KEY TAKEAWAYS
    1. [First key takeaway]
    2. [Second key takeaway]
    ...

    Keep it concise and impactful."""

            try:
                response = self._llm_model.invoke([{"role": "user", "content": prompt}])
                summary_content = response.content
                
                if format == "email":
                    # Format as professional email
                    email_content = f"""Subject: Executive Summary - {', '.join(article_titles[:2])}{'...' if len(article_titles) > 2 else ''}

    Dear Leadership Team,

    Please find below a strategic summary of the recent analysis conducted from a {role.value.replace('_', ' ')} perspective.

    {summary_content}

    SOURCES
    {chr(10).join([f'• {source}' for source in source_list])}
    {'• ... and ' + str(source_count - 3) + ' more sources' if source_count > 3 else ''}

    This analysis covered {source_count} document(s) and was prepared for {target_audience}.

    Best regards,
    {role.value.replace('_', ' ').title()}
    """
                    return email_content
                else:
                    # Return plain format
                    return summary_content
                    
            except Exception as e:
                logging.error(f"Error generating executive summary: {e}")
                
                # Fallback: Create basic summary from key insights
                fallback_summary = f"EXECUTIVE SUMMARY\n"
                fallback_summary += f"Analysis of {source_count} document(s) from a {role.value.replace('_', ' ')} perspective.\n\n"
                fallback_summary += f"KEY TAKEAWAYS\n"
                
                # Take top insights (up to max_takeaways)
                if all_insights:
                    top_insights = all_insights[:max_takeaways]
                    for i, insight in enumerate(top_insights, 1):
                        fallback_summary += f"{i}. {insight}\n"
                else:
                    fallback_summary += "Unable to extract insights due to processing error.\n"
                
                if format == "email":
                    return f"""Subject: Executive Summary - Analysis Complete

    Dear Leadership Team,

    {fallback_summary}

    SOURCES
    {chr(10).join([f'• {source}' for source in source_list])}

    Best regards,
    """
                else:
                    return fallback_summary
        
    def save_executive_summary(
        self,
        output_path: Union[str, Path],
        summary_length: int = 100,
        max_takeaways: int = 5,
        format: Literal["txt", "html"] = "txt"
    ) -> str:
        """Save executive summary email to a file for easy copy-paste into Outlook.
        
        Args:
            output_path: Path to save the email (e.g., 'executive_summary.txt')
            summary_length: Maximum length of executive summary in words (default: 100)
            max_takeaways: Maximum number of key takeaways to include (default: 5)
            format: File format - "txt" for plain text or "html" for HTML email
            
        Returns:
            Path to saved file
            
        Example:
            >>> generator.save_executive_summary('summary_email.txt', summary_length=75)
            >>> # Now open summary_email.txt and copy into Outlook
        """
        output_path = Path(output_path)
        
        # Generate the email content
        email_content = self.get_key_insights(
            summary_length=summary_length,
            max_takeaways=max_takeaways,
            format="email"
        )
        
        if format == "html":
            # Convert to HTML for rich formatting in Outlook
            html_content = self._convert_email_to_html(email_content)
            output_path.write_text(html_content, encoding='utf-8')
        else:
            # Save as plain text
            output_path.write_text(email_content, encoding='utf-8')
        
        logging.info(f"Executive summary saved to {output_path}")
        print(f"\n✅ Executive summary saved to: {output_path}")
        print(f"📧 Ready to copy-paste into Outlook!\n")
        
        return email_content
