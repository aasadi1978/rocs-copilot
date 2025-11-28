from langchain_core.messages import (
    AIMessage, 
    HumanMessage, 
    SystemMessage, 
    AnyMessage,
    ToolMessage,
    message_to_dict,
    messages_from_dict
)


def deserialize_messages(serialized: list[dict]) -> list[AnyMessage]:
    """
    Convert list of dicts back into LangChain message objects.
    Uses LangChain's built-in messages_from_dict for proper deserialization.
    """
    if not serialized:
        return []
    
    try:
        # Use LangChain's built-in deserialization which handles all message types
        # and preserves metadata, tool_calls, etc.
        return messages_from_dict(serialized)
    except Exception as e:
        # Fallback to manual deserialization for backwards compatibility
        deserialized = []
        for m in serialized:
            msg_type = m.get("type")
            content = m.get("content", "")
            
            # Extract additional fields
            kwargs = {
                "content": content,
                "additional_kwargs": m.get("additional_kwargs", {}),
                "response_metadata": m.get("response_metadata", {}),
            }
            
            if "name" in m:
                kwargs["name"] = m["name"]
            if "id" in m:
                kwargs["id"] = m["id"]
            
            if msg_type == "human":
                deserialized.append(HumanMessage(**kwargs))
            elif msg_type == "ai":
                if "tool_calls" in m:
                    kwargs["tool_calls"] = m["tool_calls"]
                deserialized.append(AIMessage(**kwargs))
            elif msg_type == "system":
                deserialized.append(SystemMessage(**kwargs))
            elif msg_type == "tool":
                kwargs["tool_call_id"] = m.get("tool_call_id", "")
                deserialized.append(ToolMessage(**kwargs))
            else:
                # fallback for unknown types
                deserialized.append(HumanMessage(**kwargs))
        
        return deserialized


def serialize_messages(messages: list[AnyMessage]) -> list[dict]:
    """
    Convert list of LangChain message objects into serializable dicts.
    Uses LangChain's built-in message_to_dict for complete serialization.
    """
    if not messages:
        return []
    
    try:
        # Use LangChain's built-in serialization which preserves all metadata
        return [message_to_dict(msg) for msg in messages]
    except Exception as e:
        # Fallback to basic serialization
        serialized = []
        for msg in messages:
            msg_dict = {
                "type": msg.type,
                "content": msg.content
            }
            
            # Preserve important metadata
            if hasattr(msg, "additional_kwargs") and msg.additional_kwargs:
                msg_dict["additional_kwargs"] = msg.additional_kwargs
            if hasattr(msg, "response_metadata") and msg.response_metadata:
                msg_dict["response_metadata"] = msg.response_metadata
            if hasattr(msg, "name") and msg.name:
                msg_dict["name"] = msg.name
            if hasattr(msg, "id") and msg.id:
                msg_dict["id"] = msg.id
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
            if hasattr(msg, "tool_call_id") and msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
            
            serialized.append(msg_dict)
        
        return serialized
