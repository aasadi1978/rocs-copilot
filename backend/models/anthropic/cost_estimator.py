"""Cost estimation module for LLM API usage.

This module provides cost estimation capabilities for various LLM providers including
Anthropic, OpenAI, and Groq models based on their current pricing.

Pricing sources (as of December 2025):
- Anthropic: https://www.anthropic.com/pricing
- OpenAI: https://openai.com/pricing
- Groq: https://groq.com/pricing
"""

from __future__ import annotations
import logging
from typing import Dict, Optional, Union, Literal, List
from dataclasses import dataclass
from datetime import datetime

# Pricing per 1M tokens (input/output) in USD
PRICING_TABLE = {
    # Anthropic models
    "claude-opus-4-1-20250805": {"input": 15.00, "output": 75.00, "provider": "anthropic"},
    "claude-sonnet-4-5": {"input": 3.00, "output": 15.00, "provider": "anthropic"},
    "claude-sonnet-3-5-20241022": {"input": 3.00, "output": 15.00, "provider": "anthropic"},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00, "provider": "anthropic"},
    "claude-haiku-3-5-20241022": {"input": 0.80, "output": 4.00, "provider": "anthropic"},
    
    # OpenAI models
    "gpt-5": {"input": 10.00, "output": 30.00, "provider": "openai"},
    "gpt-4o": {"input": 2.50, "output": 10.00, "provider": "openai"},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60, "provider": "openai"},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00, "provider": "openai"},
    "gpt-4": {"input": 30.00, "output": 60.00, "provider": "openai"},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50, "provider": "openai"},
    
    # Groq models (free tier available, these are estimated enterprise prices)
    "llama-3.1-8b-instant": {"input": 0.05, "output": 0.10, "provider": "groq"},
    "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79, "provider": "groq"},
    "llama-3.1-70b-versatile": {"input": 0.59, "output": 0.79, "provider": "groq"},
    "mixtral-8x7b-32768": {"input": 0.27, "output": 0.27, "provider": "groq"},
}


@dataclass
class CostEstimate:
    """Data class for cost estimation results."""
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    model: str
    provider: str
    timestamp: datetime
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Cost Estimate for {self.model} ({self.provider}):\n"
            f"  Input:  {self.input_tokens:,} tokens → ${self.input_cost:.6f}\n"
            f"  Output: {self.output_tokens:,} tokens → ${self.output_cost:.6f}\n"
            f"  Total:  {self.input_tokens + self.output_tokens:,} tokens → ${self.total_cost:.6f}\n"
            f"  Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "input_cost": self.input_cost,
            "output_cost": self.output_cost,
            "total_cost": self.total_cost,
            "model": self.model,
            "provider": self.provider,
            "timestamp": self.timestamp.isoformat(),
            "cost_per_1k_tokens": (self.total_cost / (self.input_tokens + self.output_tokens)) * 1000 
                if (self.input_tokens + self.output_tokens) > 0 else 0
        }


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str,
    provider: Optional[Literal["anthropic", "openai", "groq"]] = None
) -> CostEstimate:
    """
    Estimate the cost of an LLM API call based on token usage.
    
    Args:
        input_tokens: Number of input tokens used
        output_tokens: Number of output tokens generated
        model: Model name (e.g., "claude-opus-4-1-20250805", "gpt-4o-mini")
        provider: Optional provider name. If not provided, will be inferred from model name
        
    Returns:
        CostEstimate object with detailed cost breakdown
        
    Raises:
        ValueError: If model is not found in pricing table
        
    Example:
        >>> cost = estimate_cost(1000, 500, "claude-haiku-4-5-20251001")
        >>> print(cost)
        >>> print(f"Total cost: ${cost.total_cost:.4f}")
    """
    # Normalize model name
    model_normalized = model.strip().lower()
    
    # Find exact or partial match in pricing table
    pricing = None
    matched_model = None
    
    for price_model, price_data in PRICING_TABLE.items():
        if model_normalized == price_model.lower() or model_normalized in price_model.lower():
            pricing = price_data
            matched_model = price_model
            break
    
    if not pricing:
        # Try to infer provider and suggest similar models
        available_models = list(PRICING_TABLE.keys())
        raise ValueError(
            f"Model '{model}' not found in pricing table. "
            f"Available models: {', '.join(available_models)}"
        )
    
    # Get provider from pricing data or use provided
    detected_provider = pricing["provider"]
    if provider and provider != detected_provider:
        logging.warning(
            f"Provided provider '{provider}' does not match detected provider "
            f"'{detected_provider}' for model '{matched_model}'"
        )
    
    # Calculate costs (pricing is per 1M tokens)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost
    
    return CostEstimate(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost=input_cost,
        output_cost=output_cost,
        total_cost=total_cost,
        model=matched_model,
        provider=detected_provider,
        timestamp=datetime.now()
    )


def get_pricing_info(model: str) -> Dict[str, Union[str, float]]:
    """
    Get pricing information for a specific model.
    
    Args:
        model: Model name
        
    Returns:
        Dictionary with pricing information including provider, input/output costs per 1M tokens
        
    Example:
        >>> info = get_pricing_info("claude-haiku-4-5-20251001")
        >>> print(f"Input cost per 1M tokens: ${info['input']}")
    """
    model_normalized = model.strip().lower()
    
    for price_model, price_data in PRICING_TABLE.items():
        if model_normalized == price_model.lower() or model_normalized in price_model.lower():
            return {
                "model": price_model,
                "provider": price_data["provider"],
                "input_per_1m": price_data["input"],
                "output_per_1m": price_data["output"],
                "currency": "USD"
            }
    
    raise ValueError(f"Model '{model}' not found in pricing table")


def compare_model_costs(
    input_tokens: int,
    output_tokens: int,
    models: List[str]
) -> List[CostEstimate]:
    """
    Compare costs across multiple models for the same token usage.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        models: List of model names to compare
        
    Returns:
        List of CostEstimate objects sorted by total cost (lowest to highest)
        
    Example:
        >>> costs = compare_model_costs(
        ...     input_tokens=10000,
        ...     output_tokens=5000,
        ...     models=["claude-haiku-4-5-20251001", "gpt-4o-mini", "llama-3.1-8b-instant"]
        ... )
        >>> for cost in costs:
        ...     print(f"{cost.model}: ${cost.total_cost:.4f}")
    """
    estimates = []
    
    for model in models:
        try:
            estimate = estimate_cost(input_tokens, output_tokens, model)
            estimates.append(estimate)
        except ValueError as e:
            logging.warning(f"Skipping model {model}: {e}")
    
    # Sort by total cost
    return sorted(estimates, key=lambda x: x.total_cost)


def list_available_models(provider: Optional[str] = None) -> List[str]:
    """
    List all available models in the pricing table.
    
    Args:
        provider: Optional filter by provider ("anthropic", "openai", "groq")
        
    Returns:
        List of model names
        
    Example:
        >>> anthropic_models = list_available_models(provider="anthropic")
        >>> print(anthropic_models)
    """
    if provider:
        return [
            model for model, data in PRICING_TABLE.items()
            if data["provider"] == provider.lower()
        ]
    return list(PRICING_TABLE.keys())


class CostTracker:
    """Track cumulative costs across multiple API calls."""
    
    def __init__(self):
        """Initialize cost tracker."""
        self.estimates: List[CostEstimate] = []
        self.start_time = datetime.now()
    
    def add_estimate(self, estimate: CostEstimate):
        """Add a cost estimate to the tracker."""
        self.estimates.append(estimate)
    
    def add_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str,
        provider: Optional[str] = None
    ):
        """Add a new usage and calculate cost."""
        estimate = estimate_cost(input_tokens, output_tokens, model, provider)
        self.add_estimate(estimate)
        return estimate
    
    def get_total_cost(self) -> float:
        """Get total cost across all tracked estimates."""
        return sum(est.total_cost for est in self.estimates)
    
    def get_total_tokens(self) -> Dict[str, int]:
        """Get total token counts."""
        return {
            "input": sum(est.input_tokens for est in self.estimates),
            "output": sum(est.output_tokens for est in self.estimates),
            "total": sum(est.input_tokens + est.output_tokens for est in self.estimates)
        }
    
    def get_summary(self) -> Dict:
        """Get summary of all tracked costs."""
        tokens = self.get_total_tokens()
        runtime = (datetime.now() - self.start_time).total_seconds()
        
        # Group by model
        by_model = {}
        for est in self.estimates:
            if est.model not in by_model:
                by_model[est.model] = {
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost": 0.0
                }
            by_model[est.model]["calls"] += 1
            by_model[est.model]["input_tokens"] += est.input_tokens
            by_model[est.model]["output_tokens"] += est.output_tokens
            by_model[est.model]["cost"] += est.total_cost
        
        return {
            "total_cost": self.get_total_cost(),
            "total_tokens": tokens,
            "total_calls": len(self.estimates),
            "runtime_seconds": runtime,
            "by_model": by_model,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat()
        }
    
    def __str__(self) -> str:
        """Human-readable summary."""
        summary = self.get_summary()
        tokens = summary["total_tokens"]
        
        output = f"\n{'='*60}\n"
        output += f"Cost Tracker Summary\n"
        output += f"{'='*60}\n"
        output += f"Total Calls:   {summary['total_calls']}\n"
        output += f"Total Tokens:  {tokens['total']:,} (input: {tokens['input']:,}, output: {tokens['output']:,})\n"
        output += f"Total Cost:    ${summary['total_cost']:.6f}\n"
        output += f"Runtime:       {summary['runtime_seconds']:.2f} seconds\n"
        output += f"\nBreakdown by Model:\n"
        output += f"{'-'*60}\n"
        
        for model, data in summary["by_model"].items():
            output += f"{model}:\n"
            output += f"  Calls:  {data['calls']}\n"
            output += f"  Tokens: {data['input_tokens'] + data['output_tokens']:,}\n"
            output += f"  Cost:   ${data['cost']:.6f}\n"
        
        output += f"{'='*60}\n"
        return output


if __name__ == "__main__":
    # Example usage
    print("LLM Cost Estimator - Examples\n")
    
    # Example 1: Single estimate
    print("Example 1: Single cost estimate")
    cost = estimate_cost(
        input_tokens=10000,
        output_tokens=5000,
        model="claude-haiku-4-5-20251001"
    )
    print(cost)
    print()
    
    # Example 2: Compare models
    print("\nExample 2: Compare costs across models")
    comparisons = compare_model_costs(
        input_tokens=50000,
        output_tokens=25000,
        models=[
            "claude-haiku-4-5-20251001",
            "claude-sonnet-4-5",
            "gpt-4o-mini",
            "llama-3.1-8b-instant"
        ]
    )
    
    print(f"{'Model':<40} {'Total Cost':>15}")
    print("-" * 60)
    for est in comparisons:
        print(f"{est.model:<40} ${est.total_cost:>14.6f}")
    
    # Example 3: Cost tracker
    print("\n\nExample 3: Cost tracker for multiple API calls")
    tracker = CostTracker()
    
    # Simulate multiple API calls
    tracker.add_usage(5000, 2000, "claude-haiku-4-5-20251001")
    tracker.add_usage(3000, 1500, "claude-haiku-4-5-20251001")
    tracker.add_usage(8000, 4000, "claude-sonnet-4-5")
    
    print(tracker)
    
    # Example 4: List available models
    print("\nExample 4: List available models by provider")
    print("\nAnthropic models:")
    for model in list_available_models("anthropic"):
        info = get_pricing_info(model)
        print(f"  {model}: ${info['input_per_1m']:.2f}/${info['output_per_1m']:.2f} per 1M tokens")
