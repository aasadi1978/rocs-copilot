from os import getenv
import anthropic
from utils.dynamic_model_selector import create_dynamic_agent
from utils.http_client import HTTP_CLIENT
from dotenv import load_dotenv
load_dotenv()

anthropic_basic_model = anthropic.Anthropic(
    "claude-haiku-4-5",
    api_key=getenv("ANTHROPIC_API_KEY"),
    http_client=HTTP_CLIENT

)

anthropic_advanced_model = anthropic.Anthropic(
    "claude-sonnet-4-5",
    api_key=getenv("ANTHROPIC_API_KEY"),
    http_client=HTTP_CLIENT

)

dynamic_anthropic_agent =create_dynamic_agent(basic_model=anthropic_basic_model, advanced_model=anthropic_advanced_model)
