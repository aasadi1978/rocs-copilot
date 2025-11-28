import logging
from os import getenv

from langchain_groq import ChatGroq
from utils.dynamic_model_selector import create_dynamic_agent

# Modeles: https://console.groq.com/docs/models
# which one should I use?

# Ultra-cheap & fast: llama-3.1-8b-instant
# Balanced high-quality: gpt-oss-20b or llama-3.3-70b-versatile
# Max quality: gpt-oss-120b
# Built-in tools / agents: groq/compound or groq/compound-mini
# Speech-to-text: whisper-large-v3(-turbo)
# Moderation: meta-llama/llama-guard-4-12b, or preview Prompt Guard / Safety GPT-OSS


def initialize_groq_models():
    try:
        basic_llm, advanced_llm = None, None

        if getenv("GROQ_API_KEY"):
            basic_llm = ChatGroq(
                api_key=getenv("GROQ_API_KEY"),
                model="llama-3.1-8b-instant",
                temperature=0.7,
            )

            res = basic_llm.invoke("Hello, Basic GROQ!")
            if res.content:
                logging.info(f"Basic GROQ LLM response received: {res.content}")
            else:
                raise ValueError(
                    "No content received from Basic LLM invocation of GROQ."
                )

            advanced_llm = ChatGroq(
                api_key=getenv("GROQ_API_KEY"),
                model="llama-3.1-8b-instant",
                temperature=0.7,
            )

            logging.info("GROQ: LLM_MODEL_ADVANCED initialized successfully.")

        else:
            logging.warning("GROQ_API_KEY not found in environment variables.")

    except Exception as e:
        logging.error(f"GROQ: Error invoking GROQ LLMs: {str(e)}", exc_info=True)

        basic_llm = None
        advanced_llm = None

    return basic_llm, advanced_llm


groq_basic, groq_advanced = initialize_groq_models()
groq_dynamic_agent = create_dynamic_agent(basic_model=groq_basic, advanced_model=groq_advanced)