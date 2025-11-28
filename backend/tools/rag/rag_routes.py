from flask import request, jsonify, Blueprint, Response
from langchain_core.messages import HumanMessage, AIMessage
from typing import Annotated, List
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
import json
import uuid

# source_document_files = [
#     # "C:\\Users\\3626416\\Projects\\fenixbot\\docs"
#     "https://cio.economictimes.indiatimes.com/news/artificial-intelligence/from-data-to-intelligence-the-rise-of-smarter-predictive-supply-chains/125324044"
#     # "https://lilianweng.github.io/posts/2024-11-28-reward-hacking/",
#     # "https://lilianweng.github.io/posts/2024-07-07-hallucination/",
#     # "https://lilianweng.github.io/posts/2024-04-12-diffusion-video/",
# ]


rag_bp = Blueprint('rag', __name__, url_prefix='/rag')

# Pydantic model for chat state
class ChatState(BaseModel):
    """Chat state using Pydantic with add_messages for message handling."""
    messages: Annotated[List, add_messages] = Field(default_factory=list)
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    class Config:
        arbitrary_types_allowed = True

# In-memory conversation storage (replace with database in production)
conversation_store: dict[str, ChatState] = {}

def get_or_create_conversation(conversation_id: str = None) -> ChatState:
    """Get existing conversation or create a new one."""
    if conversation_id and conversation_id in conversation_store:
        return conversation_store[conversation_id]
    
    # Create new conversation
    new_conversation = ChatState()
    conversation_store[new_conversation.conversation_id] = new_conversation
    return new_conversation

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

@rag_bp.route("/chat/rag/stream", methods=["POST"])
def rag_chat_stream():
    """
    Process chatbot request with RAG workflow and stream response using Server-Sent Events.
    Uses Pydantic ChatState with add_messages for conversation management.
    """
    import logging

    wrkflow = init_workflow()
    
    data = request.json
    user_input = data.get("message", "").strip()
    conversation_id = data.get("conversation_id", "")
    
    if not user_input:
        return jsonify({"error": "Empty message", "code": 400})

    try:
        # Get or create conversation using Pydantic model
        chat_state = get_or_create_conversation(conversation_id)
        
        # Add user message using add_messages (automatically handled by Pydantic)
        chat_state.messages.append(HumanMessage(content=user_input))
        
    except Exception as e:
        return jsonify({"error": f"State init error: {str(e)}", "code": 500})

    def generate():
        nonlocal chat_state
        reply_text = ""
        
        try:
            # Stream through the RAG workflow
            for node, message in wrkflow.stream_chat(chat_state.messages):
                logging.info(f"Node: {node}")
                
                # Stream content as it's generated
                if hasattr(message, 'content') and message.content:
                    content = message.content
                    
                    # Only stream the final answer to the user
                    # Check if message has tool_calls attribute and if it's empty
                    has_tool_calls = hasattr(message, 'tool_calls') and message.tool_calls
                    
                    if node == "generate_answer" or (
                        node == "generate_query_or_respond" and 
                        not has_tool_calls
                    ):
                        # For streaming word by word or chunk by chunk
                        # you might need to modify this based on your needs
                        reply_text = content
                        yield f"data: {json.dumps({'content': content, 'node': node})}\n\n"
            
            # Update state with final response using add_messages
            if reply_text:
                chat_state.messages.append(AIMessage(content=reply_text))
                # Save to conversation store
                conversation_store[chat_state.conversation_id] = chat_state
            
            # Send completion signal
            yield f"data: {json.dumps({'done': True, 'conversation_id': chat_state.conversation_id})}\n\n"
            
        except Exception as e:
            logging.error(f"Error in RAG chat stream: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


@rag_bp.route("/chat/rag/invoke", methods=["POST"])
def rag_chat_invoke():
    """
    Process chatbot request with RAG workflow and return complete response.
    Uses Pydantic ChatState with add_messages for conversation management.
    """
    import logging
    
    wrkflow = init_workflow()
    
    data = request.json
    user_input = data.get("message", "").strip()
    conversation_id = data.get("conversation_id", "")
    
    if not user_input:
        return jsonify({"error": "Empty message", "code": 400})

    try:
        # Get or create conversation using Pydantic model
        chat_state = get_or_create_conversation(conversation_id)
        
        # Add user message using add_messages (automatically handled by Pydantic)
        chat_state.messages.append(HumanMessage(content=user_input))
        
    except Exception as e:
        return jsonify({"error": f"State init error: {str(e)}", "code": 500})

    try:
        # Invoke the RAG workflow
        result = wrkflow.invoke_chat(chat_state.messages)
        
        # Extract the final response
        final_message = result["messages"][-1]
        reply_text = final_message.content if hasattr(final_message, 'content') else str(final_message)
        
        # Update state with all messages from result using add_messages
        chat_state.messages = result["messages"]
        
        # Save to conversation store
        conversation_store[chat_state.conversation_id] = chat_state
        
        return jsonify({
            "response": reply_text,
            "conversation_id": chat_state.conversation_id,
            "success": True
        })
        
    except Exception as e:
        logging.error(f"Error in RAG chat invoke: {e}")
        return jsonify({"error": str(e), "code": 500})

