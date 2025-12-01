# Interactive Chat with Q&A, History, and RAG Integration

## Overview

The new `api.interactive_chat` module provides a unified interactive chatbot that combines:

✅ **Conversation history** - Uses your existing `api.ChatState` and `ChatStateRepository`  
✅ **Multiple modes** - Regular agent, RAG (document Q&A), or article generator  
✅ **Output evaluation** - Rate and provide feedback on responses  
✅ **Persistent sessions** - Resume conversations using conversation ID  
✅ **RAG integration** - Full integration with your RAG workflow system  

## Quick Start

### 1. Terminal-based Interactive Chat

```bash
# Regular agent chat
cd backend
python start_interactive_chat.py

# RAG mode (document Q&A)
python start_interactive_chat.py --mode rag

# Article generator mode
python start_interactive_chat.py --mode article

# Resume existing conversation
python start_interactive_chat.py --conversation-id abc-123-def
```

### 2. Python API

```python
from api.interactive_chat import start_interactive_chat

# Start new RAG chat
start_interactive_chat(mode="rag")

# Resume existing conversation
start_interactive_chat(mode="agent", conversation_id="your-conversation-id")
```

### 3. Programmatic Usage

```python
from api.interactive_chat import InteractiveChat

# Create chat instance
chat = InteractiveChat(mode="rag")

# Send messages
response = chat.chat("What are the main points in the document?")
print(response)

# View history
chat.show_history()

# Evaluate response
evaluation = chat.evaluate_last_response()

# Get conversation ID for later
conv_id = chat.get_conversation_id()
```

## Available Commands

While in interactive mode, you can use these commands:

- `/history` - Show full conversation history
- `/eval` - Evaluate the last assistant response (rate 1-5 + feedback)
- `/clear` - Clear conversation history (start fresh)
- `/exit` - Exit chat (saves automatically)

## Chat Modes

### Agent Mode (Default)
Regular chat with your configured agent (AGENT_MANAGER).

```python
start_interactive_chat(mode="agent")
```

### RAG Mode
Document-based Q&A using your RAG workflow.

```python
start_interactive_chat(mode="rag")
```

### Article Mode
Interactive Q&A about documents using the article generator.

```python
start_interactive_chat(mode="article")
```

## Integration with Existing Systems

Your interactive chat **fully integrates** with your existing `api` package:

- Uses same `ChatState` and `ChatStateRepository`
- Compatible with Flask routes (`/api/chat/stream`, `/rag/chat/rag/stream`)
- Shares conversation history across web UI and terminal chat
- Works with your existing RAG and article generator workflows

## Example Session

```
You: What are the key insights from the FedEx report?