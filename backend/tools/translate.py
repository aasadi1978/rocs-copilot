import logging
from langchain_core.messages import SystemMessage, HumanMessage
from models import llm_basic


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
        llm = llm_basic.bind(temperature=0.7)
        
        # Invoke the model
        response = llm.invoke(messages)

        system_reply = response.content.strip()
    
    except Exception as e:
        logging.error(f"Error during translation: {e}")
        system_reply = f"Error during translation: {str(e)}"
        
    return system_reply

if __name__ == "__main__":
    sample_text = (
        "Dear Team,\n\n"
        "I hope this message finds you well. I wanted to update you on our latest logistics strategies "
        "that aim to enhance our supply chain efficiency and reduce costs. "
        "Your feedback and insights will be invaluable as we move forward with these initiatives.\n\n"
        "Best regards,\n"
        "Alex"
    )
    translated = translate_text(sample_text, target_language="French")
    print("Translated Text:\n", translated)