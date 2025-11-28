import logging
from langchain_core.messages import SystemMessage, HumanMessage
from models.open_ai.openai_agent import openai_dynamic_agent as client


def translate_text(
    text: str,
    target_language: str = "French"
) -> str:
    """
    This function translates the given text using LangChain ChatAPI to the {target_language}.
    """

    try:
        logging.info(f"Translating text to {target_language} ...")
        system_message_content = (
            f"You act as a professional translator in {target_language} in the area of logistics and transportation."
            f" You understand the nuances of this field and expert in communication in C-Suite level. "
            f"Please translate the text accurately and clearly."
        )

        user_message_content = f"Please translate the following text:\n\n{text}"

        messages = [
            SystemMessage(content=system_message_content),
            HumanMessage(content=user_message_content)
        ]

        # Configure the model with temperature
        llm = client.bind(temperature=0.7)
        
        # Invoke the model
        response = llm.invoke(messages)

        system_reply = response.content.strip()
    
    except Exception as e:
        logging.error(f"Error during translation: {e}")
        system_reply = f"Error during translation: {str(e)}"
        
    return system_reply