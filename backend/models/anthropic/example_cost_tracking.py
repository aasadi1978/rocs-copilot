"""Quick example demonstrating cost estimation and usage tracking.

Run this script to see the cost estimation module in action:
    python backend/models/anthropic/example_cost_tracking.py
"""

import logging
from langchain_core.messages import HumanMessage, AIMessage
from models.anthropic import (
    count_tokens_anthropic,
    estimate_cost,
    compare_model_costs,
    list_available_models,
    UsageTracker,
    CostTracker
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def example_1_basic_cost_estimation():
    """Example 1: Basic cost estimation for a single API call."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Cost Estimation")
    print("="*70)
    
    # Simulate an API call with known token counts
    input_tokens = 10000
    output_tokens = 5000
    model = "claude-haiku-4-5-20251001"
    
    # Estimate cost
    cost = estimate_cost(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        model=model
    )
    
    print(f"\nScenario: Analysis of a 10-page document")
    print(cost)
    
    # Show as dictionary
    print("\nAs JSON:")
    import json
    print(json.dumps(cost.to_dict(), indent=2))


def example_2_token_counting():
    """Example 2: Count tokens in messages."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Token Counting")
    print("="*70)
    
    # Example messages
    messages = [
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    token_count = count_tokens_anthropic(
        messages=messages,
        system="You are a helpful geography assistant."
    )
    
    print(f"\nMessage: '{messages[0]['content']}'")
    print(f"System: 'You are a helpful geography assistant.'")
    print(f"Token count: {token_count}")
    
    # Estimate cost for this query
    # Assume 20 token response
    cost = estimate_cost(
        input_tokens=token_count,
        output_tokens=20,
        model="claude-haiku-4-5-20251001"
    )
    
    print(f"\nEstimated cost for this simple query: ${cost.total_cost:.6f}")


def example_3_model_comparison():
    """Example 3: Compare costs across different models."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Model Cost Comparison")
    print("="*70)
    
    # Scenario: Large document analysis
    input_tokens = 100000  # ~75 pages
    output_tokens = 50000  # ~37 pages of output
    
    models = [
        "claude-haiku-4-5-20251001",
        "claude-sonnet-4-5",
        "claude-opus-4-1-20250805",
        "gpt-4o-mini",
        "gpt-4o",
        "llama-3.1-8b-instant"
    ]
    
    print(f"\nScenario: Analyzing a large document")
    print(f"  Input: {input_tokens:,} tokens (~75 pages)")
    print(f"  Output: {output_tokens:,} tokens (~37 pages)")
    print(f"\nCost comparison (sorted by price):\n")
    
    comparisons = compare_model_costs(input_tokens, output_tokens, models)
    
    print(f"{'Rank':<6} {'Model':<40} {'Cost':>12} {'Provider':<12}")
    print("-" * 75)
    
    for rank, cost in enumerate(comparisons, 1):
        print(f"{rank:<6} {cost.model:<40} ${cost.total_cost:>11.4f} {cost.provider:<12}")
    
    # Show savings
    cheapest = comparisons[0]
    most_expensive = comparisons[-1]
    savings = most_expensive.total_cost - cheapest.total_cost
    savings_pct = (savings / most_expensive.total_cost) * 100
    
    print(f"\n💡 Using {cheapest.model} instead of {most_expensive.model}")
    print(f"   saves ${savings:.2f} ({savings_pct:.1f}%) per analysis!")


def example_4_usage_tracker():
    """Example 4: Track multiple API calls with UsageTracker."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Usage Tracker - Multiple API Calls")
    print("="*70)
    
    # Create tracker
    tracker = UsageTracker(model="claude-haiku-4-5-20251001")
    
    print("\nSimulating a conversation with multiple turns...\n")
    
    # Simulate conversation turns
    conversations = [
        {
            "input": [HumanMessage(content="What is machine learning?")],
            "output": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It uses algorithms to analyze data, identify patterns, and make decisions with minimal human intervention."
        },
        {
            "input": [HumanMessage(content="What are the main types?")],
            "output": "The main types of machine learning are: 1) Supervised Learning - learns from labeled data, 2) Unsupervised Learning - finds patterns in unlabeled data, 3) Reinforcement Learning - learns through trial and error with rewards, and 4) Semi-supervised Learning - combines both labeled and unlabeled data."
        },
        {
            "input": [HumanMessage(content="Give me an example of supervised learning")],
            "output": "A classic example of supervised learning is email spam detection. The algorithm is trained on a dataset of emails labeled as 'spam' or 'not spam'. It learns to identify patterns and features that distinguish spam emails, such as certain keywords, sender addresses, or formatting. Once trained, it can classify new, unseen emails as spam or legitimate."
        }
    ]
    
    for i, conv in enumerate(conversations, 1):
        cost = tracker.track_complete_call(
            input_messages=conv["input"],
            output_content=conv["output"]
        )
        print(f"Turn {i}: ${cost.total_cost:.6f}")
    
    # Show summary
    print(f"\n{tracker}")
    
    print(f"\nStatistics:")
    print(f"  Average cost per turn: ${tracker.get_average_cost_per_call():.6f}")
    print(f"  Total conversation cost: ${tracker.get_total_cost():.6f}")


def example_5_cost_tracker_multiple_models():
    """Example 5: Track costs across multiple models."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Cost Tracker - Multiple Models")
    print("="*70)
    
    tracker = CostTracker()
    
    print("\nSimulating a workflow using different models for different tasks...\n")
    
    # Simple queries with Haiku (fast, cheap)
    print("1. Quick Q&A sessions (using Haiku)...")
    for i in range(5):
        tracker.add_usage(500, 200, "claude-haiku-4-5-20251001")
    
    # Complex analysis with Sonnet (balanced)
    print("2. Document analysis (using Sonnet)...")
    for i in range(2):
        tracker.add_usage(10000, 5000, "claude-sonnet-4-5")
    
    # Critical task with Opus (highest quality)
    print("3. Critical legal review (using Opus)...")
    tracker.add_usage(15000, 8000, "claude-opus-4-1-20250805")
    
    print(f"\n{tracker}")


def example_6_list_models():
    """Example 6: List available models and pricing."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Available Models and Pricing")
    print("="*70)
    
    providers = ["anthropic", "openai", "groq"]
    
    for provider in providers:
        models = list_available_models(provider=provider)
        print(f"\n{provider.upper()} Models:")
        print("-" * 70)
        print(f"{'Model':<40} {'Input/1M':<12} {'Output/1M':<12}")
        print("-" * 70)
        
        for model in models:
            from backend.models.anthropic.cost_estimator import get_pricing_info
            info = get_pricing_info(model)
            print(f"{model:<40} ${info['input_per_1m']:<11.2f} ${info['output_per_1m']:<11.2f}")


def example_7_realistic_scenario():
    """Example 7: Realistic scenario - Article generation workflow."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Realistic Scenario - Article Generation")
    print("="*70)
    
    print("\nScenario: Generate 5 articles from research papers")
    print("  - Each paper: ~5,000 tokens")
    print("  - Each article output: ~3,000 tokens")
    print("  - Total: 5 articles\n")
    
    tracker = UsageTracker(model="claude-haiku-4-5-20251001")
    
    # Simulate article generation
    for i in range(5):
        cost = tracker.cost_tracker.add_usage(
            input_tokens=5000,
            output_tokens=3000,
            model="claude-haiku-4-5-20251001"
        )
        print(f"  Article {i+1}: ${cost.total_cost:.6f}")
    
    total = tracker.get_total_cost()
    
    print(f"\n📊 Summary:")
    print(f"  Total cost: ${total:.4f}")
    print(f"  Cost per article: ${total/5:.4f}")
    print(f"  Total tokens: {tracker.get_summary()['total_tokens']['total']:,}")
    
    # Compare with other models
    print(f"\n💰 Cost comparison for this workflow:")
    
    models_to_compare = [
        "claude-haiku-4-5-20251001",
        "claude-sonnet-4-5",
        "gpt-4o-mini",
        "llama-3.1-8b-instant"
    ]
    
    total_input = 5 * 5000
    total_output = 5 * 3000
    
    comparisons = compare_model_costs(total_input, total_output, models_to_compare)
    
    for cost in comparisons:
        savings = comparisons[-1].total_cost - cost.total_cost
        print(f"  {cost.model:<40} ${cost.total_cost:>8.4f} (save ${savings:.4f})")


def main():
    """Run all examples."""
    print("\n" + "🎯" * 35)
    print("LLM COST ESTIMATION - COMPREHENSIVE EXAMPLES")
    print("🎯" * 35)
    
    try:
        example_1_basic_cost_estimation()
        example_2_token_counting()
        example_3_model_comparison()
        example_4_usage_tracker()
        example_5_cost_tracker_multiple_models()
        example_6_list_models()
        example_7_realistic_scenario()
        
        print("\n" + "✅" * 35)
        print("All examples completed successfully!")
        print("✅" * 35 + "\n")
        
    except Exception as e:
        logging.error(f"Error running examples: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
