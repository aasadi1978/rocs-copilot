# import anthropic
from flask import request, jsonify, Blueprint, Response
from langchain_core.messages import HumanMessage


api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route("/chat/stream", methods=["POST"])
def chat_stream():
    """
    Process chatbot request and stream response using Server-Sent Events.
    """

    from api.init_state import init_state
    from models.chief_agent import AGENT_MANAGER as agent
    import logging
    
    data = request.json
    user_input = data.get("message", "").strip()
    conversation_id = data.get("conversation_id", "")
    
    # Debug: Check if agent is initialized
    if agent is None:
        logging.error("LLM_MODEL_BASIC is None - model not initialized")
        return jsonify({"error": "LLM model not initialized. Check API key and model configuration.", "code": 500})
    
    logging.info(f"Using agent: {type(agent).__name__}")
    
    if not user_input:
        return jsonify({"error": "Empty message", "code": 400})

    try:
        state, record = init_state(conversation_id=conversation_id)
        if not state:
            return jsonify({"error": "Failed to initialize state", "code": 500})
    except Exception as e:
        return jsonify({"error": f"State init error: {str(e)}", "code": 500})

    state["messages"].append(HumanMessage(content=user_input))

    def generate():

        import json
        from langchain_core.messages import AIMessage
        
        nonlocal state, record
        reply_text = ""

        import logging
        
        logging.info("Starting stream...")
        logging.info(f"Messages: {state['messages']}")
    
        try:

            for token, metadata in agent.stream(  
                {"messages": [{"role": "user", "content": user_input}]},
                stream_mode="messages",
            ):
                print(f"node: {metadata['langgraph_node']}")
                print(f"content: {token.content_blocks}")
                print("\n")

            input("Press Enter to continue...")

            # Stream directly from the chat model with the messages list
            for chunk in agent.stream(state["messages"]):
                logging.info(f"Received chunk: {chunk}")
                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                    reply_text += content
                    logging.info(f"Content: {content}")
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            # Save conversation state
            state["messages"].append(AIMessage(content=reply_text))
            record.save_state_snapshot(state)
            
            # Send final message with conversation ID
            yield f"data: {json.dumps({'done': True, 'conversation_id': record.conversation_id})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')
