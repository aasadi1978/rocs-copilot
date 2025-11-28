import logging
from tools.outlook.system_message import BUSINESS_COMMUNICATOR_SYSTEM_MESSAGE, INTERPRETOR_SYSTEM_MESSAGE
from tools.outlook.format_email import format_for_outlook
from models.open_ai.openai_agent import openai_dynamic_agent as client
from langchain_core.messages import SystemMessage, HumanMessage
from pathlib import Path


def draft_bilingual_email(target_language: str="", first_draft = "") -> str:
    """
    Draft a bilingual English and {target_language} email using the OpenAI Agent.
    """
    try:
        logging.info(f"Drafting bilingual email in {target_language} ...")
        draft_email = False
        system_reply = ""

        if first_draft == "":
            logging.info("No initial draft provided. Starting fresh email draft.")
            return

        user_content = f"Draft and email based on {first_draft}"
    
        messages = [
            SystemMessage(content=INTERPRETOR_SYSTEM_MESSAGE.format(language=target_language)),
            HumanMessage(content=user_content)
        ]

        llm = client.bind(temperature=0.2)
        response = llm.invoke(messages)
        system_reply = response.content.strip()

        logging.info("\n--- Revised Email ---\n")
        logging.info(system_reply)
        logging.info("\n" + "="*80 + "\n")

        with open("draft.txt", "w", encoding="utf-8") as f:
            f.write(system_reply)

        logging.info("Are you satisfied with the drafted email?")

        if system_reply:
            body_html = format_for_outlook(system_reply)

            return body_html

        return ""

    except Exception as e:
        logging.error(f"Error generating email: {e}")