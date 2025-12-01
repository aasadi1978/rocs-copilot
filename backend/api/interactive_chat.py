"""Interactive chat interface with Q&A, history, and RAG integration.

This module provides a terminal-based interactive chatbot that:
- Maintains conversation history using the api.ChatState system
- Integrates with RAG workflows for document-based Q&A
- Allows output evaluation and feedback
- Supports multiple chat modes (regular agent, RAG, article generator)
"""

import logging
from typing import Optional, Literal
from langchain_core.messages import HumanMessage, AIMessage
from api.chat_state_repository import ChatStateRepository
from api.init_state import init_state


class InteractiveChat:
    """Interactive chatbot with history, Q&A, and RAG integration."""
    
    def __init__(
        self, 
        mode: Literal["agent", "rag", "article"] = "agent",
        conversation_id: str = ""
    ):
        """
        Initialize interactive chat.
        
        Args:
            mode: Chat mode - "agent" (regular chat), "rag" (document Q&A), or "article" (article generator)
            conversation_id: Optional existing conversation ID to resume
        """
        self.mode = mode
        self.state = None
        self.record = None
        self.agent = None
        self.rag_workflow = None
        self.article_generator = None
        
        # Initialize state
        self._init_conversation(conversation_id)
        
        # Initialize the appropriate chat backend
        if mode == "agent":
            self._init_agent()
        elif mode == "rag":
            self._init_rag()
        elif mode == "article":
            self._init_article_generator()
    
    def _init_conversation(self, conversation_id: str):
        """Initialize or load conversation state."""
        self.state, self.record = init_state(conversation_id)
        if not self.state:
            raise ValueError("Failed to initialize chat state")
        
        logging.info(f"Chat initialized. Conversation ID: {self.record.conversation_id}")
        logging.info(f"History: {len(self.state['messages'])} messages")
    
    def _init_agent(self):
        """Initialize the default agent."""
        from models import llm_basic as AGENT_MANAGER
        self.agent = AGENT_MANAGER
        if not self.agent:
            raise ValueError("Agent not initialized. Check model configuration.")
        logging.info(f"Using agent: {type(self.agent).__name__}")
    
    def _init_rag(self):
        """Initialize RAG workflow."""
        from tools.rag.workflow import RAG_WORKFLOW_INSTANCE
        
        # Check if already initialized, otherwise initialize with default sources
        if not RAG_WORKFLOW_INSTANCE._documents:
            print("\n⚠️  RAG workflow not initialized. Please provide document sources:")
            print("Example: ['path/to/doc.pdf', 'https://example.com/article']")
            sources = input("Enter sources (comma-separated) or press Enter for default: ").strip()
            
            if sources:
                source_list = [s.strip() for s in sources.split(',')]
            else:
                # Default sources
                source_list = ["https://www.youtube.com/watch?v=JTwxQbUFJhc"]
            
            print(f"Initializing RAG with sources: {source_list}")
            RAG_WORKFLOW_INSTANCE.initialize(
                data_sources=source_list,
                name="RAG_Retriever",
                description="Retrieves relevant documents for question answering"
            )
            RAG_WORKFLOW_INSTANCE.build_graph()
        
        self.rag_workflow = RAG_WORKFLOW_INSTANCE
        logging.info("RAG workflow initialized")
    
    def _init_article_generator(self):
        """Initialize article generator."""
        from tools.article_generator import ArticleGenerator, ArticleRole
        from pathlib import Path
        
        print("\n⚠️  Article generator mode requires documents. Please provide:")
        sources = input("Enter document paths (comma-separated): ").strip()
        
        if not sources:
            raise ValueError("Article generator requires document sources")
        
        source_list = [Path(s.strip()) for s in sources.split(',')]
        
        role = input("Enter role (journalist/analyst/consultant/technical_writer) [journalist]: ").strip() or "journalist"
        
        self.article_generator = ArticleGenerator()
        self.article_generator.initialize(
            documents=source_list,
            role=ArticleRole(role.lower()),
            article_style="conversational",
            target_audience="general audience",
            article_length="medium"
        )
        self.article_generator.build_graph()
        logging.info("Article generator initialized")
    
    def chat(self, user_input: str) -> str:
        """
        Send a message and get response.
        
        Args:
            user_input: User's message
            
        Returns:
            Assistant's response
        """
        # Add user message to state
        self.state["messages"].append(HumanMessage(content=user_input))
        
        # Get response based on mode
        if self.mode == "agent":
            response = self._chat_with_agent()
        elif self.mode == "rag":
            response = self._chat_with_rag()
        elif self.mode == "article":
            response = self._chat_with_article_generator()
        else:
            raise ValueError(f"Unknown mode: {self.mode}")
        
        # Add assistant response to state
        self.state["messages"].append(AIMessage(content=response))
        
        # Save state
        self.record.save_state_snapshot(self.state)
        
        return response
    
    def _chat_with_agent(self) -> str:
        """Chat using the default agent."""
        result = self.agent.invoke({"messages": self.state["messages"]})
        
        if "messages" in result:
            return result["messages"][-1].content
        else:
            return str(result)
    
    def _chat_with_rag(self) -> str:
        """Chat using RAG workflow."""
        result = self.rag_workflow.invoke_chat(self.state["messages"])
        return result["messages"][-1].content
    
    def _chat_with_article_generator(self) -> str:
        """Chat using article generator."""
        result = self.article_generator.invoke_chat(self.state["messages"])
        return result["messages"][-1].content
    
    def show_history(self):
        """Display conversation history."""
        print("\n" + "="*80)
        print("CONVERSATION HISTORY")
        print("="*80 + "\n")
        
        for i, msg in enumerate(self.state["messages"], 1):
            role = "USER" if msg.type == "human" else "ASSISTANT"
            print(f"[{i}] {role}: {msg.content[:100]}...")
            print()
    
    def evaluate_last_response(self) -> dict:
        """
        Evaluate the last assistant response.
        
        Returns:
            Dictionary with evaluation metrics
        """
        if len(self.state["messages"]) < 2:
            return {"error": "No response to evaluate"}
        
        last_response = self.state["messages"][-1]
        if last_response.type != "ai":
            return {"error": "Last message is not from assistant"}
        
        print("\n" + "="*80)
        print("EVALUATE RESPONSE")
        print("="*80 + "\n")
        print(f"Response: {last_response.content}\n")
        
        # Get user feedback
        rating = input("Rate response (1-5): ").strip()
        feedback = input("Feedback (optional): ").strip()
        
        evaluation = {
            "rating": int(rating) if rating.isdigit() else None,
            "feedback": feedback,
            "response_length": len(last_response.content),
            "conversation_id": self.record.conversation_id
        }
        
        print(f"\n✓ Evaluation recorded: {evaluation}")
        return evaluation
    
    def clear_history(self):
        """Clear conversation history (start fresh)."""
        confirm = input("Clear conversation history? (yes/no): ").strip().lower()
        if confirm == "yes":
            self.state["messages"] = []
            self.record.save_state_snapshot(self.state)
            print("✓ History cleared")
    
    def get_conversation_id(self) -> str:
        """Get current conversation ID."""
        return self.record.conversation_id
    
    def run_interactive_loop(self):
        """Run the main interactive chat loop."""
        print("\n" + "="*80)
        print(f"INTERACTIVE CHAT - Mode: {self.mode.upper()}")
        print("="*80)
        print(f"Conversation ID: {self.record.conversation_id}")
        print(f"Messages in history: {len(self.state['messages'])}")
        print("\nCommands:")
        print("  /history  - Show conversation history")
        print("  /eval     - Evaluate last response")
        print("  /clear    - Clear conversation history")
        print("  /exit     - Exit chat")
        print("="*80 + "\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    if user_input == "/exit":
                        print(f"\n✓ Chat saved. Conversation ID: {self.record.conversation_id}")
                        break
                    elif user_input == "/history":
                        self.show_history()
                    elif user_input == "/eval":
                        self.evaluate_last_response()
                    elif user_input == "/clear":
                        self.clear_history()
                    else:
                        print(f"Unknown command: {user_input}")
                    continue
                
                # Get response
                print("\nAssistant: ", end="", flush=True)
                response = self.chat(user_input)
                print(response + "\n")
                
            except KeyboardInterrupt:
                print(f"\n\n✓ Chat interrupted. Conversation ID: {self.record.conversation_id}")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                logging.error(f"Chat error: {e}", exc_info=True)


def start_interactive_chat(
    mode: Literal["agent", "rag", "article"] = "agent",
    conversation_id: str = ""
):
    """
    Start an interactive chat session.
    
    Args:
        mode: Chat mode - "agent" (regular), "rag" (document Q&A), or "article" (article generator)
        conversation_id: Optional conversation ID to resume
    
    Example:
        # Start new chat with default agent
        start_interactive_chat(mode="agent")
        
        # Resume existing conversation with RAG
        start_interactive_chat(mode="rag", conversation_id="abc-123")
        
        # Start article generator chat
        start_interactive_chat(mode="article")
    """
    chat = InteractiveChat(mode=mode, conversation_id=conversation_id)
    chat.run_interactive_loop()


if __name__ == "__main__":
    # Example: Start interactive chat with RAG
    start_interactive_chat(mode="rag")
