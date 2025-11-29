from utils.dynamic_model_selector import create_dynamic_agent
from utils.http_client import ASYNC_HTTP_CLIENT, HTTP_CLIENT
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import logging
from os import getenv
from dotenv import load_dotenv
load_dotenv(override=True)


def setup_openai_llms():
    """Initialize LLM models based on available OPENAI_API keys if available."""
    basic_llm, advanced_llm = None, None

    if getenv('OPENAI_API_KEY'):

        try:
            basic_llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=getenv('OPENAI_API_KEY'),
                http_client=HTTP_CLIENT,
                http_async_client=ASYNC_HTTP_CLIENT
            )

            # print(getenv('OPENAI_API_KEY'))
            # res = basic_llm.invoke("Hello, Basic OpenAI!")
            # if res.content:
            #     logging.info(f"Basic OpenAI LLM response received: {res.content}")
            # else:
            #     raise ValueError("No content received from Basic OpenAI LLM invocation.")
            
            # input("Press Enter to continue...")

        except Exception as e:
            logging.error(f"Error invoking OpenAI: basic_llm: {e}")
            basic_llm = None

        try:
            advanced_llm = ChatOpenAI(
            model="gpt-5",
            api_key=getenv('OPENAI_API_KEY'),
            http_client=HTTP_CLIENT,
            http_async_client=ASYNC_HTTP_CLIENT
            )
            logging.info("OpenAI: LLM_MODEL_ADVANCED initialized successfully.")

        except Exception as e:
            logging.error(f"Error invoking OpenAI: advanced_llm: {e}")
            advanced_llm = None
            basic_llm = None
    
    else:
        logging.warning("OPENAI_API_KEY not found in environment variables.")

    return basic_llm, advanced_llm

openai_basic, openai_advanced = setup_openai_llms()

dynamic_openai_agent = create_dynamic_agent(basic_model=openai_basic, advanced_model=openai_advanced)

logging.info("Testing OpenAI dynamic agent...")
if openai_basic is None:
    logging.warning("OpenAI basic model is not initialized. Cannot test dynamic agent.")
    raise ValueError("OpenAI basic model is not initialized. Cannot test dynamic agent.")

response = dynamic_openai_agent.invoke({
    "messages": [HumanMessage(content="Hello, OpenAI!")]
})

if "messages" in response:
    logging.info("\nResponse:")
    for msg in response["messages"]:
        logging.info(f"{msg.type}: {msg.content}")
else:
    logging.info(response)