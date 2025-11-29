"""News Tracker Agent - Summarizes news articles using existing RAG infrastructure."""

# Initialize with news URLs
from pathlib import Path
from tools.news_tracker.news_summarizer import NewsSummarizer


summarizer = NewsSummarizer()
summarizer.initialize(news_urls=[
    # 'https://www.linkedin.com/posts/fernandomanso1970_fedex-dataworks-and-servicenow-unite-ai-activity-7391928752777236484-Z2TI?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAFY6MoBPxjxfWtkDOBzPxWtbRqvNKTLmsU'
    # 'https://newsroom.fedex.com/newsroom/global-english/fedex-dataworks-and-servicenow-unite-ai-data-and-workflows-to-power-supply-chains-of-the-future'
    # 'https://www.forbes.com/councils/forbesbusinesscouncil/2025/11/26/how-europe-can-prepare-young-professionals-for-the-ai-economy/'
    # 'https://cio.economictimes.indiatimes.com/news/artificial-intelligence/from-data-to-intelligence-the-rise-of-smarter-predictive-supply-chains/125324044'
    # 'https://www.deeplearning.ai/the-batch/issue-329/'
    # Path().resolve() / 'docs'/ 'Ng-AI-bubble.docx'
    # 'https://www.youtube.com/watch?v=XeUAu65unu8'
    Path().resolve() / 'docs' / '2025-FedEx-Global-Economic-Impact-Report.pdf'
])

# Get summaries and digest (no graph needed)
summaries = summarizer.get_summaries()

# Save summaries to markdown file
with open('summaries.md', 'w', encoding='utf-8') as f:
    f.write("# Article Summaries\n\n")
    
    for i, summary in enumerate(summaries, 1):
        f.write(f"## {i}. {summary['title']}\n\n")
        f.write(f"**Source:** {summary['url']}\n\n")
        if summary.get('publish_date'):
            f.write(f"**Published:** {summary['publish_date']}\n\n")
        f.write(f"**Topics:** {summary['topics']}\n\n")
        f.write(f"### Summary\n\n{summary['summary']}\n\n")
        f.write(f"### Key Points\n\n")
        for point in summary['key_points']:
            f.write(f"- {point}\n")
        f.write("\n---\n\n")

print("✓ Summaries saved to summaries.md")

print("--------------------------------------------")
digest = summarizer.get_digest()
print("News Digest:", digest)

# Save to markdown file
with open('digest.md', 'w', encoding='utf-8') as f:
    f.write(digest)

print("--------------------------------------------")

# Create a Twitter post from the first article
post = summarizer.create_social_media_post(platform="twitter", tone="engaging")

# Create a LinkedIn post from the second article without hashtags
post = summarizer.create_social_media_post(
    platform="linkedin", 
    summary_index=0, 
    max_length=280,
    include_hashtags=True,
    tone="professional"
)

print("Social Media Post:", post)
print("--------------------------------------------")

# summarizer.assemble_decision_flow()

# # Build graph for interactive Q&A
# summarizer.display_state_graph(graph_name="news_workflow")

# print("--------------------Chatbot------------------")
# # Ask questions about the news
# result = summarizer.invoke_chat([{
#     "role": "user", 
#     "content": "What are the main political stories?"
# }])

# # Or use streaming
# for node, message in summarizer.stream_chat([{...}]):
#     print(f"{node}: {message.content}")
