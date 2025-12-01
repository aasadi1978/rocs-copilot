"""Launch interactive chat from command line.

Usage:
    # Regular agent chat
    python start_interactive_chat.py
    
    # RAG mode (document Q&A)
    python start_interactive_chat.py --mode rag
    
    # Article generator mode
    python start_interactive_chat.py --mode article
    
    # Resume existing conversation
    python start_interactive_chat.py --conversation-id abc-123-def
"""

import argparse
import logging
from api.interactive_chat import start_interactive_chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s | %(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    parser = argparse.ArgumentParser(description="Interactive Chat with History and RAG")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["agent", "rag", "article"],
        default="agent",
        help="Chat mode: agent (default), rag (document Q&A), or article (article generator)"
    )
    parser.add_argument(
        "--conversation-id",
        type=str,
        default="",
        help="Resume existing conversation by ID"
    )
    
    args = parser.parse_args()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║          ROCS COPILOT - Interactive Chat                     ║
╚══════════════════════════════════════════════════════════════╝
Mode: {args.mode.upper()}
{"Conversation ID: " + args.conversation_id if args.conversation_id else "New Conversation"}
""")
    
    start_interactive_chat(mode=args.mode, conversation_id=args.conversation_id)

if __name__ == "__main__":
    main()
