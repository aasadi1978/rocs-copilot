import logging
from anthropic import Anthropic
from os import getenv
from typing import Dict, List, Union
from langchain_core.messages import AnyMessage
from dotenv import load_dotenv
from langchain_core.documents import Document

load_dotenv()

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=getenv("ANTHROPIC_API_KEY"))

def count_tokens_anthropic(
    messages: Union[List[Dict[str, str]], List[AnyMessage], List[Document]], 
    system: str = "",
    tools: List[Dict[str, str]] = []
) -> int:
    """
    Count tokens in messages for Anthropic models.
    
    Args:
        messages: List of message dicts OR LangGraph AnyMessage objects OR LangChain Document objects
        system: System message for context
        tools: List of tool descriptions for context
        
    Returns:
        int: Total token count
    """
    try:
        # Handle empty messages
        if not messages:
            return 0
            
        # Detect input type and convert to required format
        first_item = messages[0]
        
        if isinstance(first_item, Document):
            # For Document objects, count tokens in page_content
            # Create a single user message with all document content
            combined_content = "\n\n".join(doc.page_content for doc in messages)
            formatted_messages = [{"role": "user", "content": combined_content}]
            
        elif isinstance(first_item, dict):
            # Already in correct format
            formatted_messages = messages
            
        elif hasattr(first_item, "type") and hasattr(first_item, "content"):
            # Convert AnyMessage objects (HumanMessage, AIMessage, etc.)
            formatted_messages = [
                {
                    "role": "assistant" if msg.type == "ai" else msg.type,
                    "content": msg.content
                }
                for msg in messages
            ]
        else:
            raise ValueError(f"Unsupported message type: {type(first_item)}")
        
        response = anthropic_client.messages.count_tokens(
            model="claude-sonnet-4-5",
            system=system or "You are a scientist.",
            tools=tools,
            messages=formatted_messages,
        )
        return response.input_tokens
        
    except Exception as e:
        logging.error(f"Error counting tokens: {e}")
        return 0