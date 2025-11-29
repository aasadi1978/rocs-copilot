from flask import Flask

def register_all_tools(app: Flask):
    """Register tools with the application context."""
    with app.app_context():

        from tools import TOOLS
        from models.groq.get_models import get_groq_models
        from tools.outlook.draft_email import draft_bilingual_email
        from tools.translate import translate_text
        from tools.outlook.format_email import format_for_outlook

        TOOLS.register_tools(tools=[
            get_groq_models, 
            draft_bilingual_email,
            translate_text,
            format_for_outlook])