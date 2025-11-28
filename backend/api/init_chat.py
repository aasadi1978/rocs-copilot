from os import getenv
# import anthropic
from api.chat_state import ChatState
from flask import request, jsonify, Blueprint, Response
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, AnyMessage
from api.chat_state_repository import ChatStateRepository

from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages

api_bp = Blueprint('api', __name__, url_prefix='/api')

def create_initial_state(conversation_id: str) -> ChatState:
    """Create an initial chat state; or load from a database in production."""
    ChatStateRepository.load_chat_state(conversation_id=conversation_id) if conversation_id \
        else ChatStateRepository.initialize_chat_session()

def init_workflow():
    """Initialize the RAG workflow singleton."""
    from tools.rag.workflow import RAG_WORKFLOW_INSTANCE

    # Configure your data sources
    source_document_files = [
        # "https://cio.economictimes.indiatimes.com/news/artificial-intelligence/from-data-to-intelligence-the-rise-of-smarter-predictive-supply-chains/125324044",
        "https://www.youtube.com/watch?v=JTwxQbUFJhc"
        # Add more sources as needed:
        # "C:\\Users\\3626416\\Projects\\fenixbot\\docs",
        # "https://your-url-here.com",
    ]

    print("Initializing RAG workflow...")
    RAG_WORKFLOW_INSTANCE.initialize(
        data_sources=source_document_files,
        name="RAG_Retriever",
        description="Retrieves relevant documents from FenixBot knowledge base for question answering"
    )

    RAG_WORKFLOW_INSTANCE.build_graph()

    return RAG_WORKFLOW_INSTANCE