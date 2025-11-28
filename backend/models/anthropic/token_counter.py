import logging
from models.anthropic import dynamic_anthropic_agent as client
from typing import List, Dict

def count_tokens_anthropic(messages: List[Dict[str, str]], system: str, client=client) -> int:
    """
    Count the number of tokens in a list of messages for a given Anthropic model.
    
    Args:
        messages (list): A list of message dictionaries with 'role' and 'content'.
        system (str): The system message to provide context for the conversation.
    Example:
        ```bash

        response = client.messages.count_tokens(
            system="You are a scientist",
            messages=[{
                "role": "user",
                "content": "Hello, Claude"
            }],
        )

        data = response.json()
        print(f"Total tokens: {data['total_tokens']}")

        return int(data['total_tokens'])

        ```

    Returns:
        int: The total number of tokens in the messages.
    """

    try:
        response = client.messages.count_tokens(
            system=system or "You are a helpful assistant.",
            messages=messages,
        )

        return int(response.json()['total_tokens'])
    except Exception as e:
        logging.error(f"Error counting tokens with Anthropic: {e}")
        return 0