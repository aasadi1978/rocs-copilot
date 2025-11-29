"""Article generation prompts with configurable professional roles."""

from typing import Literal, Dict
from enum import Enum


class ArticleRole(str, Enum):
    """Predefined professional roles for article generation."""
    FINANCIAL_ADVISOR = "financial_advisor"
    JOURNALIST = "journalist"
    SCIENTIFIC_RESEARCHER = "scientific_researcher"
    BUSINESS_ANALYST = "business_analyst"
    TECHNICAL_WRITER = "technical_writer"
    MARKETING_SPECIALIST = "marketing_specialist"
    POLICY_ANALYST = "policy_analyst"
    HEALTHCARE_EXPERT = "healthcare_expert"
    LEGAL_ANALYST = "legal_analyst"
    EDUCATOR = "educator"
    CUSTOM = "custom"
    MCKINSEY_CONSULTANT = "mckinsey_consultant"
    DELOITTE_CONSULTANT = "deloitte_consultant"


# Role definitions with professional context
ROLE_DEFINITIONS: Dict[str, str] = {
    ArticleRole.FINANCIAL_ADVISOR: """You are a professional financial advisor with expertise in investment strategies, 
market analysis, and financial planning. You provide clear, actionable insights for investors and financial professionals.""",

    ArticleRole.MCKINSEY_CONSULTANT: """You are a McKinsey analyst/consultant specializing in supply chain and logistics business strategy, market trends, and management 
consulting. You conduct a deep analysis of complex business challenges, identify key issues, and develop actionable strategies. You provide insightful, data-driven 
analysis to help businesses optimize their operations and strategies.""",
    
    ArticleRole.DELOITTE_CONSULTANT: """You are a Deloitte analyst/consultant with expertise in supply chain management, logistics optimization, and business transformation. 
You deliver strategic insights and practical recommendations to help organizations enhance their supply chain performance and resilience.""",
    
    ArticleRole.JOURNALIST: """You are a professional journalist with experience in investigative reporting and 
news writing. You deliver objective, well-researched articles that inform and engage readers with compelling narratives.""",
    
    ArticleRole.SCIENTIFIC_RESEARCHER: """You are a scientific researcher with expertise in translating complex 
research into accessible insights. You maintain academic rigor while making scientific concepts understandable to broader audiences.""",
    
    ArticleRole.BUSINESS_ANALYST: """You are a business analyst specializing in market trends, competitive analysis, 
and strategic insights. You provide data-driven perspectives that help businesses make informed decisions.""",
    
    ArticleRole.TECHNICAL_WRITER: """You are a technical writer who excels at explaining complex technical concepts 
in clear, precise language. You create documentation and articles that help readers understand technology and processes.""",
    
    ArticleRole.MARKETING_SPECIALIST: """You are a marketing specialist with expertise in content strategy, 
brand storytelling, and audience engagement. You create compelling content that resonates with target audiences.""",
    
    ArticleRole.POLICY_ANALYST: """You are a policy analyst with expertise in government, regulations, and public affairs. 
You provide insightful analysis on policy implications and their impact on various stakeholders.""",
    
    ArticleRole.HEALTHCARE_EXPERT: """You are a healthcare expert with deep knowledge of medical science, 
healthcare systems, and patient care. You communicate health information accurately and accessibly.""",
    
    ArticleRole.LEGAL_ANALYST: """You are a legal analyst with expertise in interpreting laws, regulations, 
and legal precedents. You provide clear analysis of legal issues and their practical implications.""",
    
    ArticleRole.EDUCATOR: """You are an educator skilled at breaking down complex topics into digestible lessons. 
You create educational content that facilitates learning and understanding.""",
}


def get_role_context(role: ArticleRole, custom_role_description: str = None) -> str:
    """
    Get the professional context for a given role.
    
    Args:
        role: The ArticleRole enum value
        custom_role_description: Custom role description if role is CUSTOM
        
    Returns:
        Role context string
        
    Raises:
        ValueError: If role is CUSTOM but no custom_role_description provided
    """
    if role == ArticleRole.CUSTOM:
        if not custom_role_description:
            raise ValueError("custom_role_description is required when using ArticleRole.CUSTOM")
        return custom_role_description
    
    return ROLE_DEFINITIONS.get(role, ROLE_DEFINITIONS[ArticleRole.JOURNALIST])


def generate_article_prompt(
    role_context: str,
    document_content: str,
    article_style: Literal["formal", "conversational", "technical", "persuasive"] = "formal",
    target_audience: str = "general audience",
    article_length: Literal["short", "medium", "long"] = "medium",
    focus_areas: str = None
) -> str:
    """
    Generate the article creation prompt based on role and parameters.
    
    Args:
        role_context: Professional role context (from get_role_context)
        document_content: Source document content to analyze
        article_style: Writing style for the article
        target_audience: Intended audience description
        article_length: Desired article length
        focus_areas: Optional specific areas to focus on
        
    Returns:
        Formatted prompt string
    """
    
    length_guidance = {
        "short": "Write a concise article (500-800 words) that captures the key insights.",
        "medium": "Write a comprehensive article (1000-1500 words) with detailed analysis.",
        "long": "Write an in-depth article (2000-3000 words) with thorough exploration of all aspects."
    }
    
    style_guidance = {
        "formal": "Use a formal, professional tone with precise language and structured arguments.",
        "conversational": "Use a conversational, engaging tone that connects with readers personally.",
        "technical": "Use technical precision with industry-specific terminology and detailed explanations.",
        "persuasive": "Use persuasive language that builds compelling arguments and calls to action."
    }
    
    focus_instruction = f"\n\nSpecific Focus Areas: {focus_areas}" if focus_areas else ""
    
    return f"""{role_context}

Analyze the following document and create a professional article based on your expertise:

=== SOURCE DOCUMENT ===
{document_content}
===================

Article Requirements:
- Target Audience: {target_audience}
- Writing Style: {style_guidance.get(article_style, style_guidance["formal"])}
- Length: {length_guidance.get(article_length, length_guidance["medium"])}{focus_instruction}

Create an article that:
1. Provides a compelling title that captures the essence
2. Opens with an engaging introduction
3. Presents key insights and analysis from your professional perspective
4. Includes relevant examples, data points, or evidence from the source
5. Organizes content with clear sections and logical flow
6. Concludes with actionable takeaways or thought-provoking insights
7. Maintains consistency with your professional role and expertise

Format your response as a structured article with:
- title: A compelling article title
- introduction: Opening paragraph(s)
- main_sections: Array of section objects with 'heading' and 'content'
- conclusion: Closing thoughts and takeaways
- key_insights: List of 3-5 main insights
- tags: Relevant topic tags/keywords
"""


def generate_digest_prompt(
    role_context: str,
    articles_summary: str,
    digest_focus: str = "key themes and insights"
) -> str:
    """
    Generate prompt for creating a digest from multiple articles.
    
    Args:
        role_context: Professional role context
        articles_summary: Combined summary of all articles
        digest_focus: What to focus on in the digest
        
    Returns:
        Formatted digest prompt
    """
    return f"""{role_context}

Based on your professional expertise, create a comprehensive digest from the following article summaries.

=== ARTICLE SUMMARIES ===
{articles_summary}
========================

Create a professional digest that:
1. Identifies and highlights {digest_focus}
2. Groups related insights by topic or theme
3. Provides your expert perspective and analysis
4. Draws connections between different articles
5. Offers strategic recommendations or conclusions
6. Is well-organized and actionable

Format the digest in **Markdown** with:
- A compelling title (# heading)
- Executive summary section
- Thematic sections with ## headings
- Bullet points for key insights
- Bold text for emphasis
- Clear, professional structure
"""


def generate_qa_prompt(
    role_context: str,
    question: str,
    context: str,
    article_summaries: str = None
) -> str:
    """
    Generate prompt for answering questions based on articles and context.
    
    Args:
        role_context: Professional role context
        question: User's question
        context: Retrieved context from documents
        article_summaries: Optional article summaries for additional context
        
    Returns:
        Formatted Q&A prompt
    """
    summaries_section = f"\n\nAvailable Article Summaries:\n{article_summaries}" if article_summaries else ""
    
    return f"""{role_context}

Answer the following question based on your professional expertise and the provided context.
Provide clear, accurate information drawing from your domain knowledge.

Question: {question}

Context: {context}{summaries_section}

Provide a professional, well-reasoned response that:
- Directly addresses the question
- Draws on the provided context and your expertise
- Includes relevant examples or evidence
- Acknowledges limitations or uncertainties when appropriate
- Offers actionable insights when relevant
"""
