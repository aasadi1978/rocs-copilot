def get_summarizer_prompt(instruction: str, article) -> str:
    """Generate the news summarization prompt with specified instruction level."""

    try:
        title = article.metadata.get('title', 'Untitled')
        source = article.metadata.get('source', 'Unknown Source')
        page_content = article.page_content or ''

        return f"""You are a professional world-class news analyst. Analyze the following news article and provide a structured summary.

Article Title: {title}
Article URL: {source}

Article Content:
{page_content}

Provide:
1. summary: {instruction}
2. key_points: A list of 3-5 key points (as an array of strings, not bullet points)
3. topics: Comma-separated main topics/categories (e.g., technology, politics, business, etc.)

Ensure key_points is returned as an array/list of strings, not as formatted text.
"""
    except Exception as e:
        return f"Error generating prompt: {e}"

def get_digest_prompt(combined_text: str) -> str:
    """Generate the news digest prompt based on article summaries."""

    return f"""You are a news editor creating a daily news digest. Based on the following article summaries, 
create a comprehensive news digest that:
1. Highlights the most important stories
2. Groups related stories by topic
3. Provides context and connections between stories
4. Is well-organized and easy to read

Here are the article summaries:

{combined_text}

Create a professional news digest in **Markdown format** with:
- A title (# heading)
- Clear sections with ## headings for different topics
- Bullet points for key information
- Bold text for emphasis where appropriate
- Well-structured and easy to read
"""

def generate_answer_prompt(question: str, context: str, summaries: str) -> str:
    """Generate the prompt for answering questions based on news article summaries."""

    return f"""You are a world-class news analyst assistant. Answer questions about news articles. "
"Use the following retrieved context and summaries to answer the question. "
"Provide clear, factual information. If you don't know, say so.\n\n"
"Question: {question}\n"
"Context: {context}\n\n"
"Available Summaries:\n{summaries}"""
        