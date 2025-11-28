# from models.anthropic import basic_model_name as llm_basic, advanced_model_name as llm_advanced
# from models.open_ai.openai_agent import OpenAI_Agent as DynamicAgent
# llm_basic, llm_advanced = setup_openai_llms()
# from models.anthropic import Anthropic_Client as DynamicAgent
# from langchain.chat_models import init_chat_model
# llm_basic = init_chat_model(llm_basic)
# llm_advanced = init_chat_model(llm_advanced)

from models.anthropic import anthropic_basic_model as llm_basic, anthropic_advanced_model as llm_advanced
