

from tools.translate import translate_text


AI_DISCLAIMER = """
<hr style="border:none; border-top:1px solid #cccccc; margin-top:12px; margin-bottom:12px;">
<p style="font-size:10pt; font-family:FedEx Sans, Calibri, sans-serif; color:#666666;">
<b>Disclaimer / Avertissement :</b><br>
The French version of this message was generated using AI. While it aims to be accurate and well-structured, translation or phrasing errors may occur. 
We appreciate your feedback if you notice any issues.<br>
La version française de ce message a été générée à l'aide de l'intelligence artificielle. 
Bien qu'elle vise à être précise et bien structurée, des erreurs de traduction ou de formulation peuvent survenir. 
Nous vous remercions par avance pour tout retour si vous en constatez.
</p>
"""

SUBJECT_DISCLAIMER = "Disclaimer / Avertissement"

AI_DISCLAIMER_EN = """The {target_language} version of this message was generated using AI. While it aims to be accurate and well-structured, translation or phrasing errors may occur. 
We appreciate your feedback if you notice any issues."""

AI_DISCLAIMER_BILINGUAL = """
<hr style="border:none; border-top:1px solid #cccccc; margin-top:12px; margin-bottom:12px;">
<p style="font-size:10pt; font-family:FedEx Sans, Calibri, sans-serif; color:#666666;">
<b>Disclaimer / Avertissement :</b><br>
The {target_language} version of this message was generated using AI. While it aims to be accurate and well-structured, translation or phrasing errors may occur. 
We appreciate your feedback if you notice any issues.<br>
{translated}
</p>
"""

def get_disclaimer_in_language(target_language: str = "") -> str:

    if not target_language:
        return ""

    subject = f"Disclaimer / {translate_text(text='Disclaimer', target_language=target_language)}"
    disclaimer_msg = AI_DISCLAIMER.format(target_language=target_language)
    translated = translate_text(text=disclaimer_msg, target_language=target_language)

    AI_DISCLAIMER_BILINGUAL = f"""
    <hr style="border:none; border-top:1px solid #cccccc; margin-top:12px; margin-bottom:12px;">
    <p style="font-size:10pt; font-family:FedEx Sans, Calibri, sans-serif; color:#666666;">
    <b>{subject} :</b><br>
    {disclaimer_msg}<br>
    {translated}
    </p>
    """

    return AI_DISCLAIMER_BILINGUAL
