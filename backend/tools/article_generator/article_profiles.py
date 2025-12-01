from tools.article_generator.article_prompts import ArticleRole
from pathlib import Path

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