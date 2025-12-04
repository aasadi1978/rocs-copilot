from tools.article_generator.article_prompts import ArticleRole
from pathlib import Path

FEDEX_FIN_STATUS = {
    "filename": 'annual-fin-summary',
    "role": ArticleRole.MCKINSEY_CONSULTANT,
    "article_style": "formal",
    "target_audience": "FedEx Express leadership team",
    "article_length": "short",
    "focus_areas": "FedEx Financial Status, challenges and growth and profitability in Europe, recommendations for strategic investments",
    "consolidate_docs": True,
    'output_path': Path().resolve() / 'rag-output'/ 'annual-report',
    "digest_opportunities_focus": "FedEx Financial Status, challenges and growth and profitability in Europe",
    "documents": [
        Path().resolve() / 'docs'/ 'fedex-reports' / 'Annual-Report-FY25.pdf',
    ],
}


FEDEX_AI_ACTIVITIES = {
    "filename": 'fedex-sme-survey-summary',
    "role": ArticleRole.JOURNALIST,
    "article_style": "formal",
    "target_audience": "FedEx Express leadership team",
    "article_length": "short",
    "focus_areas": "FedEx growth and profitability in Europe, the impact of AI and automation on logistics, recommendations for strategic investments",
    "consolidate_docs": True,
    'output_path': Path().resolve() / 'rag-output'/ 'sme-survey',
    "digest_opportunities_focus": "FedEx growth opportunities and strategic recommendations for profitability of FedEx Express in Europe",
    "documents": [
        Path().resolve() / 'docs'/ 'fedex-reports' / 'Peak+research+report_FINAL+1.pdf',
        'https://emerj.com/artificial-intelligence-at-fedex/',
        'https://newsroom.fedex.com/newsroom/asia-pacific/fedex-launches-ai-powered-sorting-robot-to-drive-smart-logistics',
        'https://newsroom.fedex.com/newsroom/global/elroyair',
        Path().resolve() / 'docs'/ 'fedex-reports' / 'Annual-Report-FY25.pdf',
        # 'https://www.linkedin.com/pulse/fedexs-strategic-expansion-asia-europe-trade-enhanced-asadi-phd-gubye'
    ],
}


FEDEX_SME_SURVEY = {
    "filename": 'fedex-sme-survey-summary',
    "role": ArticleRole.BUSINESS_ANALYST,
    "article_style": "formal",
    "target_audience": "FedEx Express leadership team",
    "article_length": "short",
    "focus_areas": "FedEx growth and profitability in Europe, the impact of AI and automation on logistics, recommendations for strategic investments",
    "consolidate_docs": True,
    'output_path': Path().resolve() / 'rag-output'/ 'sme-survey',
    "digest_opportunities_focus": "FedEx growth opportunities and strategic recommendations for profitability of FedEx Express in Europe",
    "documents": [
        Path().resolve() / 'docs'/ 'fedex-reports' / 'Peak+research+report_FINAL+1.pdf',
        'https://newsroom.fedex.com/newsroom/europe-english/fedex-survey-reveals-85-of-apac-smes-confident-in-europe-trade-growth',
        'https://newsroom.fedex.com/newsroom/asia-english/fedex-enhances-china-to-europe-capacity-by-adding-five-weekly-flights',
        'https://newsroom.fedex.com/newsroom/asia-english/fedex-enhances-network-from-northern-vietnam-to-asia-and-europe',
        'https://www.gov.cn/lianbo/fabu/202507/content_7031904.htm'
        # 'https://www.linkedin.com/pulse/fedexs-strategic-expansion-asia-europe-trade-enhanced-asadi-phd-gubye'
    ],
}

FEDEX_GLOBAL_ECONOMY_IMPACT= {
    "filename": 'fedex-glbl-economy-ai-impact-report-summary',
    "role": ArticleRole.MCKINSEY_CONSULTANT,
    "article_style": "formal",
    "target_audience": "FedEx Express leadership team",
    "article_length": "short",
    "focus_areas": "FedEx growth and profitability in Europe, the impact of AI and automation on logistics, recommendations for strategic investments",
    "consolidate_docs": True,
    'output_path': Path().resolve() / 'rag-output'/ 'fdx-glbl-eco-ai-report',
    "digest_opportunities_focus": "FedEx growth opportunities and strategic recommendations for profitability of FedEx Express in Europe",
    "documents": [
        Path().resolve() / 'docs'/ 'ai' / 'the-state-of-ai-in-2025-agents-innovation-and-transformation.pdf',
        Path().resolve() / 'docs'/ 'fedex-reports' / '2025-FedEx-Global-Economic-Impact-Report.pdf',
        Path().resolve() / 'docs'/ 'fedex-reports' / 'en-fr_pdf_na_CDG_impact.pdf',
    ],
}

OR_AI_LLM= {
    "filename": 'or-ai-llm-mck-summary',
    "role": ArticleRole.MCKINSEY_CONSULTANT,
    "article_style": "formal",
    "target_audience": "Data science and Operations Research professionals",
    "article_length": "short",
    "focus_areas": "Answer the question whether LLMs can enhance traditional OR methods",
    "consolidate_docs": True,
    'output_path': Path().resolve() / 'rag-output'/ 'or-ai-llm-mck-summary',
    "digest_opportunities_focus": "Answer the question whether LLMs can enhance traditional OR methods",
    "documents": [
        'https://www.youtube.com/watch?v=wP6vPTuGghw',
        Path().resolve() / 'docs'/ 'llm-or' / 'Heuristics with LLMs.pdf',
        Path().resolve() / 'docs'/ 'llm-or' / 'OR-LLM.pdf',
        Path().resolve() / 'docs'/ 'llm-or' / 'OR-LLM-2.pdf',
        Path().resolve() / 'docs'/ 'llm-or' / '5639_Chain_of_Experts_When_LLM.pdf',
        'https://www.youtube.com/watch?v=CFp80r1LWvQ'
    ],
    "References": [
        'https://www.youtube.com/watch?v=wP6vPTuGghw',
        'Heuristics with LLMs - https://arxiv.org/abs/2305.10411',
        'OR-LLM - https://arxiv.org/abs/2305.15024',
        'OR-LLM-2 - https://arxiv.org/abs/2306.14855',
        'Chain of Experts: When LLMs Meet Combinatorial Optimization - https://arxiv.org/abs/2310.06323',
        'https://www.youtube.com/watch?v=CFp80r1LWvQ'
    ]
}

AD_HOC_SUMMERIZER= {
    "filename": 'article-summerizer',
    "role": ArticleRole.MCKINSEY_CONSULTANT,
    "article_style": "formal",
    "target_audience": "FedEx Express leadership team",
    "article_length": "short",
    "focus_areas": "Executive summary and key insights from the document; potential use cases in FedEx operations",
    "consolidate_docs": True,
    'output_path': Path().resolve() / 'rag-output'/ 'article-summerizer',
    "digest_opportunities_focus": "Executive summary and key insights from the document",
    "documents": [
        Path().resolve() / 'docs'/ 'ortec' / "27_11_2025 - Let's talk AI - presenter slides.pdf",
    ],
    "References": []
}



