"""Integrated usage and cost tracking for LLM API calls.

This module combines token counting with cost estimation to provide comprehensive
tracking of LLM API usage and associated costs.
"""

from __future__ import annotations
import logging
from typing import Dict, List, Union, Optional
from langchain_core.messages import AnyMessage
from langchain_core.documents import Document

try:
    from .token_counter import count_tokens_anthropic
    from .cost_estimator import (
        estimate_cost,
        CostEstimate,
        CostTracker
    )
except ImportError:
    from models.anthropic.token_counter import count_tokens_anthropic
    from models.anthropic.cost_estimator import (
        estimate_cost,
        CostEstimate,
        CostTracker
    )


class UsageTracker:
    """
    Comprehensive tracker for LLM usage combining token counting and cost estimation.
    
    Example:
        >>> tracker = UsageTracker(model="claude-haiku-4-5-20251001")
        >>> 
        >>> # Track input before API call
        >>> tracker.track_input(messages=user_messages)
        >>> 
        >>> # Make API call
        >>> response = llm.invoke(messages)
        >>> 
        >>> # Track output after API call
        >>> tracker.track_output(response_content)
        >>> 
        >>> # Get summary
        >>> print(tracker.get_summary())
    """
    _instance = None
    _model: str = ""
    _provider: Optional[str] = None
    _initialized: bool = False
    _calls: List[Dict] = []

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super(UsageTracker, cls).__new__(cls)
            cls._instance._cost_tracker = CostTracker()
            cls._instance._calls = []
            cls._instance._model = ""
            cls._instance._provider = None
            cls._instance._initialized = False

        return cls._instance
    
    def __init__(self):
       pass
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance of UsageTracker."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self, model: str, provider: Optional[str] = None):
        """
        Re-initialize the tracker with a new model and provider.
        
        Args:
            model: Model name
            provider: Optional provider name
        """
        self._model = model
        self._provider = provider
        self._cost_tracker = CostTracker()
        self._calls = []
        logging.info(f"Re-initialized UsageTracker for model: {model}")
    
    @property
    def calls(self) -> List[Dict]:
        """Get list of tracked API calls."""
        return self._calls

    def track_input(
        self,
        messages: Union[List[Dict[str, str]], List[AnyMessage], List[Document]],
        system: str = "",
        tools: List[Dict[str, str]] = []
    ) -> int:
        """
        Track input tokens for a request.
        
        Args:
            messages: Messages to send to the API
            system: System message
            tools: Tool descriptions
            
        Returns:
            Number of input tokens
        """
        input_tokens = count_tokens_anthropic(messages, system, tools)
        
        # Store for later completion
        self._pending_input_tokens = input_tokens
        
        logging.debug(f"Tracked input: {input_tokens} tokens")
        return input_tokens
    
    def track_output(self, output_content: str, model: str | None = None) -> CostEstimate:
        """
        Track output tokens and calculate cost for a complete API call.
        
        Args:
            output_content: The generated output content
            
        Returns:
            CostEstimate for this API call
        """
        # Count output tokens (approximate)
        output_tokens = self._estimate_output_tokens(output_content)
        
        # Get input tokens from pending
        input_tokens = getattr(self, '_pending_input_tokens', 0)
        
        # Calculate cost
        cost = self._cost_tracker.add_usage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model if model is not None else self._model,
            provider=self._provider
        )
        
        # Record the call
        self._calls.append({
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": cost.total_cost,
            "timestamp": cost.timestamp,
            "model": model if model is not None else self._model
        })
        
        # Clear pending
        self._pending_input_tokens = 0
        
        logging.info(
            f"API call completed - Input: {input_tokens}, Output: {output_tokens}, "
            f"Cost: ${cost.total_cost:.6f}"
        )
        
        return cost
    
    def track_complete_call(
        self,
        input_messages: Union[List[Dict[str, str]], List[AnyMessage], List[Document]],
        output_content: str,
        system: str = "",
        tools: List[Dict[str, str]] = [],
        model: str | None = None
    ) -> CostEstimate:
        """
        Track a complete API call (input + output) in one method.
        
        Args:
            input_messages: Input messages
            output_content: Generated output
            system: System message
            tools: Tool descriptions
            model: Optional model name
            
        Returns:
            CostEstimate for this API call
        """
        self.track_input(input_messages, system, tools)
        return self.track_output(output_content=output_content, model=model)
    
    def track_with_response_metadata(
        self,
        input_messages: Union[List[Dict[str, str]], List[AnyMessage], List[Document]],
        response_metadata: Dict,
        system: str = "",
        tools: List[Dict[str, str]] = []
    ) -> CostEstimate:
        """
        Track usage using response metadata from LangChain/API response.
        
        Args:
            input_messages: Input messages
            response_metadata: Metadata from API response containing token counts
            system: System message
            tools: Tool descriptions
            
        Returns:
            CostEstimate for this API call
            
        Example:
            >>> response = llm.invoke(messages)
            >>> tracker.track_with_response_metadata(
            ...     input_messages=messages,
            ...     response_metadata=response.response_metadata
            ... )
        """
        # Try to get token counts from metadata
        input_tokens = response_metadata.get('usage', {}).get('input_tokens')
        output_tokens = response_metadata.get('usage', {}).get('output_tokens')
        
        # Fallback to counting if not in metadata
        if input_tokens is None:
            input_tokens = count_tokens_anthropic(input_messages, system, tools)
            logging.debug("Input tokens not in metadata, counted manually")
        
        if output_tokens is None:
            # This shouldn't happen with proper response metadata
            logging.warning("Output tokens not in metadata, estimation may be inaccurate")
            output_tokens = 0
        
        # Calculate cost
        cost = self._cost_tracker.add_usage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=self._model,
            provider=self._provider
        )
        
        # Record the call
        self._calls.append({
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": cost.total_cost,
            "timestamp": cost.timestamp,
            "from_metadata": True
        })
        
        logging.info(
            f"API call completed (from metadata) - Input: {input_tokens}, "
            f"Output: {output_tokens}, Cost: ${cost.total_cost:.6f}"
        )
        
        return cost
    
    def _estimate_output_tokens(self, text: str) -> int:
        """
        Estimate output tokens from text.
        
        This is a rough estimation. For accurate counts, use response metadata.
        
        Args:
            text: Output text
            
        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token on average
        return len(text) // 4
    
    def get_summary(self) -> Dict:
        """Get comprehensive summary of usage and costs."""
        return self._cost_tracker.get_summary()
    
    def get_total_cost(self) -> float:
        """Get total cost of all tracked API calls."""
        return self._cost_tracker.get_total_cost()
    
    def get_call_count(self) -> int:
        """Get number of API calls tracked."""
        return len(self._calls)
    
    def get_average_cost_per_call(self) -> float:
        """Get average cost per API call."""
        if not self._calls:
            return 0.0
        return self.get_total_cost() / len(self._calls)
    
    def reset(self):
        """Reset the tracker."""
        self._cost_tracker = CostTracker()
        self._calls = []
        self._pending_input_tokens = 0
        logging.info("UsageTracker reset")
        self._instance = None
    
    def __str__(self) -> str:
        """Human-readable summary."""
        summary = self.get_summary()
        return str(self._cost_tracker)

USAGE_TRACKER_INSTANCE = UsageTracker.get_instance()

def create_tracker(model: str, provider: Optional[str] = None) -> UsageTracker:
    """
    Convenience function to create a usage tracker.
    
    Args:
        model: Model name
        provider: Optional provider name
        
    Returns:
        UsageTracker instance
    """
    return UsageTracker(model=model, provider=provider)


if __name__ == "__main__":
    # Example usage
    from langchain_core.messages import HumanMessage, AIMessage
    
    print("Usage Tracker - Example\n")
    
    # Create tracker
    tracker = UsageTracker(model="claude-haiku-4-5-20251001")
    
    # Simulate API call 1
    print("Simulating API call 1...")
    messages1 = [
        HumanMessage(content="What is the capital of France?")
    ]
    tracker.track_input(messages1)
    
    # Simulate response
    response1 = "The capital of France is Paris."
    cost1 = tracker.track_output(response1)
    print(f"Call 1 cost: ${cost1.total_cost:.6f}\n")
    
    # Simulate API call 2
    print("Simulating API call 2...")
    messages2 = [
        HumanMessage(content="Write a short poem about Python programming.")
    ]
    response2 = """Python, elegant and clean,
    Code flows like a dream.
    Indentation makes it clear,
    Simplicity we hold dear."""
    
    cost2 = tracker.track_complete_call(messages2, response2)
    print(f"Call 2 cost: ${cost2.total_cost:.6f}\n")
    
    # Get summary
    print("\nTracker Summary:")
    print(tracker)
    
    print(f"\nAverage cost per call: ${tracker.get_average_cost_per_call():.6f}")
