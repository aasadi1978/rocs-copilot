
from tools.outlook.signature import SIGNATURE
from tools.outlook.disclaimer import get_disclaimer_in_language

def format_for_outlook(body_html: str, target_language="") -> str:
    """
    Wrap LLM-generated HTML in Outlook-friendly, compact spacing. If target_language is specified.
    Make sure to append the AI disclaimer in that language.
    """

    AI_DISCLAIMER = get_disclaimer_in_language(target_language=target_language)

    body_html = body_html.replace("html```", "").replace("```", "")
    outlook_html = f"""
    <div style="font-family:'FedEx Sans', Calibri, sans-serif; font-size:11pt; color:#000;
                line-height:1.25; mso-line-height-rule:exactly;">
        <style>
            body, div, p, ul, li {{
                font-family:'FedEx Sans', Calibri, sans-serif;
                font-size:11pt;
                color:#000;
                line-height:1.25;
                margin:0;
                padding:0;
                mso-line-height-rule:exactly;
            }}
            ul, ol {{
                margin: 4px 0 4px 18px;
                padding-left: 18px;
            }}
            li {{
                margin: 2px 0;
                line-height:1.25;
            }}
            strong {{
                color:#4D148C;
                font-weight:bold;
            }}
        </style>

        {body_html}
        <br><br>{SIGNATURE}<br>{AI_DISCLAIMER}
    </div>
    """
    return outlook_html