# import anthropic
from langchain_core.messages import AnyMessage

from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    """Represents the state of a chat session."""
    messages: Annotated[List[AnyMessage], add_messages]
    conversation_id: str
    user_id: str
    timestamp: str
