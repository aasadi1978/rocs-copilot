import logging
from langchain.agents import create_agent
from langchain.agents.middleware import (wrap_model_call, 
                                         ModelRequest, 
                                         ModelResponse, 
                                         LLMToolSelectorMiddleware,
                                         LLMToolEmulator)

from tools import TOOLS

always_include = ["search"]

def create_dynamic_agent(**kwargs):
    """Create an agent that dynamically selects models based on conversation complexity."""

    advanced_model =  kwargs.get("advanced_model") 
    basic_model =  kwargs.get("basic_model")

    try:
    
        if not basic_model and not advanced_model:
            return None
        
        @wrap_model_call
        def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
            """Choose model based on conversation complexity."""
            message_count = len(request.state["messages"])

            if message_count > 10:
                model = advanced_model
            else:
                model = basic_model

            return handler(request.override(model=model))


        if not basic_model and advanced_model:
            logging.info(f"Creating agent with only advanced model only: {str(advanced_model)}.")
            return create_agent(
                model=advanced_model,
                tools=TOOLS.tools,
                middleware=[
                    LLMToolEmulator(),
                    LLMToolSelectorMiddleware(model=advanced_model, always_include=["search"])
                ]
            )


        if basic_model and not advanced_model:
            logging.info(f"Creating agent with only basic model only: {str(basic_model)}.")
            return create_agent(
                model=basic_model,
                tools=TOOLS.tools,
                middleware=[
                    LLMToolEmulator(),
                    LLMToolSelectorMiddleware(model=basic_model, always_include=["search"])
                ]
            )
        
        return create_agent(
            model=basic_model,  # Default model
            tools=TOOLS.tools,
            middleware=[dynamic_model_selection,
                        LLMToolEmulator(),
                        LLMToolSelectorMiddleware(model=basic_model, always_include=["search"])
                        ]
        )

    except Exception as e:
        logging.error(f"Error creating dynamic agent: {e}")
        return None