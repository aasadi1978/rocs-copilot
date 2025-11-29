import logging
from os import getenv
from langchain_anthropic import ChatAnthropic
from utils.dynamic_model_selector import create_dynamic_agent
from langchain_core.messages import HumanMessage
# from utils.http_client import HTTP_CLIENT
from dotenv import load_dotenv
load_dotenv()

# Get API key from environment
api_key = getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError(
        "ANTHROPIC_API_KEY not found in environment variables. "
        "Please create a .env file with ANTHROPIC_API_KEY=your-key-here"
    )

anthropic_basic_model = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    temperature=0.7,
    max_tokens=2048,  # Increased for news summarization tasks
    timeout=None,
    max_retries=2,
    api_key=api_key
    # model_kwargs={ "http_client": HTTP_CLIENT }
)

anthropic_advanced_model = ChatAnthropic(
    model="claude-sonnet-4-5-20251022",
    temperature=0.7,
    max_tokens=1024,
    timeout=None,
    max_retries=2,
    api_key=api_key
    # model_kwargs={ "http_client": HTTP_CLIENT }
)

dynamic_anthropic_agent = create_dynamic_agent(
    basic_model=anthropic_basic_model,
    advanced_model=anthropic_advanced_model
)

logging.info("Anthropic models initialized successfully.") 


response = dynamic_anthropic_agent.invoke({
    "messages": [HumanMessage(content="Hello, Anthropic!")]
})

if "messages" in response:
    logging.info("\nResponse:")
    for msg in response["messages"]:
        logging.info(f"{msg.type}: {msg.content}")
else:
    logging.info(response)