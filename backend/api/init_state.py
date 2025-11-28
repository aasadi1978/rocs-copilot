from backend.api.chat_state_repository import ChatStateRepository
import logging

def init_state(conversation_id: str = ""):
    """Initialize or load existing ChatState."""

    try:
        record = None
        if conversation_id != "":
            # Load the latest ChatState snapshot for this conversation
            state = ChatStateRepository.load_chat_state(conversation_id)
            if state:
                record = ChatStateRepository.query.filter(
                    ChatStateRepository.conversation_id == conversation_id
                ).order_by(ChatStateRepository.timestamp.desc()).first()

        if not record:
            # Create new conversation
            record = ChatStateRepository.initialize_chat_session()
            state = record.to_chat_state()

        return state, record
    
    except Exception as e:
        logging.error(f"Error loading conversation state: {e}")
        return None, None