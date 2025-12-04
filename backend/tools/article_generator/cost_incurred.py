from models.anthropic.cost_estimator import CostEstimate, estimate_cost

def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> CostEstimate:
    """Calculate and return the cost incurred for given token usage and model."""

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