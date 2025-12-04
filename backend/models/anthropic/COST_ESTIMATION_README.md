# Cost Estimation and Usage Tracking

This module provides comprehensive cost estimation and usage tracking for LLM API calls across multiple providers (Anthropic, OpenAI, Groq).

## Features

- **Token Counting**: Accurate token counting for Anthropic models
- **Cost Estimation**: Calculate costs based on current pricing for all major LLM providers
- **Usage Tracking**: Track cumulative usage and costs across multiple API calls
- **Model Comparison**: Compare costs across different models for the same workload
- **Cost History**: Maintain detailed history of all API calls and associated costs

## Modules

### 1. `token_counter.py`
Counts tokens for Anthropic models using the official API.

```python
from backend.models.anthropic import count_tokens_anthropic

# Count tokens in messages
tokens = count_tokens_anthropic(
    messages=[{"role": "user", "content": "Hello, how are you?"}],
    system="You are a helpful assistant.",
    tools=[]
)
print(f"Token count: {tokens}")
```

### 2. `cost_estimator.py`
Estimates costs based on token usage and current pricing.

#### Basic Cost Estimation

```python
from backend.models.anthropic import estimate_cost

# Estimate cost for a single API call
cost = estimate_cost(
    input_tokens=10000,
    output_tokens=5000,
    model="claude-haiku-4-5-20251001"
)

print(cost)
# Output:
# Cost Estimate for claude-haiku-4-5-20251001 (anthropic):
#   Input:  10,000 tokens → $0.008000
#   Output: 5,000 tokens → $0.020000
#   Total:  15,000 tokens → $0.028000
```

#### Compare Models

```python
from backend.models.anthropic import compare_model_costs

# Compare costs across different models
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

for cost in comparisons:
    print(f"{cost.model}: ${cost.total_cost:.4f}")

# Output (sorted by cost):
# llama-3.1-8b-instant: $0.005000
# gpt-4o-mini: $0.022500
# claude-haiku-4-5-20251001: $0.140000
# claude-sonnet-4-5: $0.525000
```

#### Get Pricing Information

```python
from backend.models.anthropic import get_pricing_info, list_available_models

# List all available models
all_models = list_available_models()
print(f"Available models: {all_models}")

# List models by provider
anthropic_models = list_available_models(provider="anthropic")
openai_models = list_available_models(provider="openai")
groq_models = list_available_models(provider="groq")

# Get pricing details for a specific model
pricing = get_pricing_info("claude-haiku-4-5-20251001")
print(f"Input cost: ${pricing['input_per_1m']} per 1M tokens")
print(f"Output cost: ${pricing['output_per_1m']} per 1M tokens")
```

#### Cost Tracker

```python
from backend.models.anthropic import CostTracker

# Create a cost tracker
tracker = CostTracker()

# Add multiple API calls
tracker.add_usage(5000, 2000, "claude-haiku-4-5-20251001")
tracker.add_usage(3000, 1500, "claude-haiku-4-5-20251001")
tracker.add_usage(8000, 4000, "claude-sonnet-4-5")

# Get summary
print(tracker)
# Output:
# ============================================================
# Cost Tracker Summary
# ============================================================
# Total Calls:   3
# Total Tokens:  23,500 (input: 16,000, output: 7,500)
# Total Cost:    $0.057800
# Runtime:       0.12 seconds
#
# Breakdown by Model:
# ------------------------------------------------------------
# claude-haiku-4-5-20251001:
#   Calls:  2
#   Tokens: 11,500
#   Cost:   $0.014400
# claude-sonnet-4-5:
#   Calls:  1
#   Tokens: 12,000
#   Cost:   $0.084000
# ============================================================

# Get total cost
total = tracker.get_total_cost()
print(f"Total cost: ${total:.6f}")

# Get detailed summary as dict
summary = tracker.get_summary()
print(f"Total calls: {summary['total_calls']}")
print(f"By model: {summary['by_model']}")
```

### 3. `usage_tracker.py`
Combines token counting and cost estimation for comprehensive usage tracking.

#### Basic Usage

```python
from backend.models.anthropic import UsageTracker
from langchain_core.messages import HumanMessage

# Create tracker for a specific model
tracker = UsageTracker(model="claude-haiku-4-5-20251001")

# Track input before API call
messages = [HumanMessage(content="What is the capital of France?")]
tracker.track_input(messages)

# Make API call (your code)
response = llm.invoke(messages)

# Track output after API call
cost = tracker.track_output(response.content)
print(f"This call cost: ${cost.total_cost:.6f}")

# Get summary
print(tracker)
```

#### Track Complete Call

```python
from backend.models.anthropic import UsageTracker
from langchain_core.messages import HumanMessage

tracker = UsageTracker(model="claude-haiku-4-5-20251001")

# Track input and output together
messages = [HumanMessage(content="Write a haiku about Python")]
response_content = "Code flows clean and neat\nIndentation guides the way\nPython's simple grace"

cost = tracker.track_complete_call(
    input_messages=messages,
    output_content=response_content
)

print(f"Cost: ${cost.total_cost:.6f}")
```

#### Using Response Metadata

```python
from backend.models.anthropic import UsageTracker

tracker = UsageTracker(model="claude-haiku-4-5-20251001")

# Make API call
response = llm.invoke(messages)

# Track using response metadata (most accurate)
cost = tracker.track_with_response_metadata(
    input_messages=messages,
    response_metadata=response.response_metadata
)

print(f"Exact cost from API metadata: ${cost.total_cost:.6f}")
```

#### Multiple Calls Tracking

```python
from backend.models.anthropic import create_tracker
from langchain_core.messages import HumanMessage

# Create tracker
tracker = create_tracker(model="claude-haiku-4-5-20251001")

# Simulate multiple API calls
for i in range(10):
    messages = [HumanMessage(content=f"Question {i}")]
    tracker.track_input(messages)
    
    # Your API call here
    response = llm.invoke(messages)
    
    tracker.track_output(response.content)

# Get statistics
print(f"Total calls: {tracker.get_call_count()}")
print(f"Total cost: ${tracker.get_total_cost():.6f}")
print(f"Average cost per call: ${tracker.get_average_cost_per_call():.6f}")

# Get full summary
summary = tracker.get_summary()
print(f"\nDetailed Summary:")
print(f"  Total tokens: {summary['total_tokens']['total']:,}")
print(f"  Runtime: {summary['runtime_seconds']:.2f}s")
```

## Pricing Information

The cost estimator includes pricing for the following models (as of December 2025):

### Anthropic Models
| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| claude-opus-4-1-20250805 | $15.00 | $75.00 |
| claude-sonnet-4-5 | $3.00 | $15.00 |
| claude-haiku-4-5-20251001 | $0.80 | $4.00 |

### OpenAI Models
| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| gpt-5 | $10.00 | $30.00 |
| gpt-4o | $2.50 | $10.00 |
| gpt-4o-mini | $0.15 | $0.60 |
| gpt-3.5-turbo | $0.50 | $1.50 |

### Groq Models
| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| llama-3.1-8b-instant | $0.05 | $0.10 |
| llama-3.3-70b-versatile | $0.59 | $0.79 |
| mixtral-8x7b-32768 | $0.27 | $0.27 |

## Integration with Existing Code

### Example: Article Generator Integration

```python
from tools.article_generator import ArticleGenerator
from backend.models.anthropic import UsageTracker

# Create article generator with cost tracking
generator = ArticleGenerator()
tracker = UsageTracker(model="claude-haiku-4-5-20251001")

# Initialize and track
generator.initialize(
    documents=['report.pdf'],
    role=ArticleRole.FINANCIAL_ADVISOR
)

# Track the generation
articles = generator.get_articles()

# Estimate cost (you would integrate this into the actual API calls)
# This is a simplified example
for article in articles:
    estimated_tokens_in = 5000  # Based on document size
    estimated_tokens_out = len(article['content']) // 4
    
    cost = tracker.track_complete_call(
        input_messages=[{"role": "user", "content": "Generate article"}],
        output_content=article['content']
    )

print(f"Total article generation cost: ${tracker.get_total_cost():.4f}")
```

### Example: RAG System Integration

```python
from backend.models.anthropic import UsageTracker
from tools.rag import RAG_System

tracker = UsageTracker(model="claude-sonnet-4-5")

# Track each RAG query
def query_with_tracking(question: str, rag_system):
    # Track input
    tracker.track_input([{"role": "user", "content": question}])
    
    # Run RAG
    response = rag_system.query(question)
    
    # Track output
    cost = tracker.track_output(response)
    
    return response, cost

# Use it
response, cost = query_with_tracking("What are the key findings?", rag_system)
print(f"Query cost: ${cost.total_cost:.6f}")
```

## Advanced Features

### Budget Monitoring

```python
from backend.models.anthropic import UsageTracker

class BudgetMonitor:
    def __init__(self, max_budget: float, model: str):
        self.max_budget = max_budget
        self.tracker = UsageTracker(model=model)
    
    def check_budget(self) -> bool:
        return self.tracker.get_total_cost() < self.max_budget
    
    def get_remaining_budget(self) -> float:
        return max(0, self.max_budget - self.tracker.get_total_cost())
    
    def track_call(self, input_tokens: int, output_tokens: int):
        if not self.check_budget():
            raise ValueError("Budget exceeded!")
        return self.tracker.cost_tracker.add_usage(
            input_tokens, output_tokens, self.tracker.model
        )

# Use it
monitor = BudgetMonitor(max_budget=10.0, model="claude-haiku-4-5-20251001")

try:
    for i in range(1000):
        cost = monitor.track_call(input_tokens=1000, output_tokens=500)
        print(f"Call {i}: ${cost.total_cost:.6f}, Remaining: ${monitor.get_remaining_budget():.6f}")
except ValueError as e:
    print(f"Stopped: {e}")
```

### Export Cost Reports

```python
import json
from backend.models.anthropic import UsageTracker

tracker = UsageTracker(model="claude-haiku-4-5-20251001")

# ... perform multiple API calls ...

# Export summary as JSON
summary = tracker.get_summary()
with open('cost_report.json', 'w') as f:
    json.dump(summary, f, indent=2)

# Export individual estimates
cost_details = [est.to_dict() for est in tracker.cost_tracker.estimates]
with open('cost_details.json', 'w') as f:
    json.dump(cost_details, f, indent=2)
```

## Testing

Run the example scripts to test the modules:

```bash
# Test cost estimator
python -m backend.models.anthropic.cost_estimator

# Test usage tracker
python -m backend.models.anthropic.usage_tracker
```

## Notes

- **Accuracy**: Token counts for Anthropic models use the official API and are accurate. For other providers, counts are estimated.
- **Pricing**: Pricing information is current as of December 2025. Always verify with the provider's official pricing page.
- **Updates**: To update pricing, edit the `PRICING_TABLE` in `cost_estimator.py`.

## Future Enhancements

- [ ] Add support for more providers (Cohere, AI21, etc.)
- [ ] Automatic pricing updates from provider APIs
- [ ] Cost prediction based on prompt length before API call
- [ ] Integration with billing/analytics dashboards
- [ ] Rate limiting based on cost thresholds
- [ ] Multi-currency support
