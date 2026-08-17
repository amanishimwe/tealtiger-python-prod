"""This file is for testing the pricing module, by verifying the pricing data is correct and complete."""

import pytest

from tealtiger.cost import CostTracker
from tealtiger.cost.pricing import get_model_pricing
from tealtiger.cost.types import TokenUsage

# Keep this table in sync with pricing.py
MISTRAL_PRICING = [
    ("mistral-small", 0.001, 0.003),
    ("mistral-small-latest", 0.00015, 0.0006),
    ("mistral-medium", 0.0027, 0.0081),
    ("mistral-medium-latest", 0.0015, 0.0075),
    ("mistral-large", 0.004, 0.012),
    ("mistral-large-latest", 0.0005, 0.0015),
    ("mixtral-8x7b", 0.0007, 0.0007),
    ("mixtral-8x22b", 0.002, 0.006),
    # add when present in pricing.py:
    # ("open-mistral-nemo", 0.00015, 0.00015),
    # ("codestral-latest", 0.0003, 0.0009),
]
GEMINI_PRICING = [
    ("gemini-2.5-flash", 0.0003, 0.0025),
    ("gemini-2.5-pro", 0.00125, 0.01),
    ("gemini-3.5-flash", 0.0015, 0.009),
    ("gemini-3.6-flash", 0.0015, 0.0075),
]


@pytest.mark.parametrize("model,input_rate,output_rate", MISTRAL_PRICING)
def test_mistral_pricing_lookup(model, input_rate, output_rate):
    pricing = get_model_pricing(model)
    assert pricing is not None
    assert pricing.provider == "mistral"
    assert pricing.input_cost_per_1k == input_rate
    assert pricing.output_cost_per_1k == output_rate


# this test is for verifying the cost calculation for mistral-large-latest
def test_mistral_large_latest_cost_calculation():
    """Cost calculation for mistral-large-latest."""
    tracker = CostTracker()
    tokens = TokenUsage(input_tokens=1000, output_tokens=1000, total_tokens=2000)
    estimate = tracker.estimate_cost("mistral-large-latest", tokens)
    assert estimate.breakdown.input_cost == pytest.approx(0.0005)
    assert estimate.breakdown.output_cost == pytest.approx(0.0015)
    assert estimate.estimated_cost == pytest.approx(0.002)


@pytest.mark.parametrize("model,input_rate,output_rate", GEMINI_PRICING)
def test_gemini_pricing_lookup(model, input_rate, output_rate):
    pricing = get_model_pricing(model)
    assert pricing is not None
    assert pricing.provider == "google"
    assert pricing.input_cost_per_1k == input_rate
    assert pricing.output_cost_per_1k == output_rate


def test_gemini_2_5_pro_cost_calculation():
    """Cost for 1000 in + 1000 out on gemini-2.5-pro."""
    tracker = CostTracker()
    tokens = TokenUsage(input_tokens=1000, output_tokens=1000, total_tokens=2000)
    estimate = tracker.estimate_cost("gemini-2.5-pro", tokens)
    assert estimate.breakdown.input_cost == pytest.approx(0.00125)
    assert estimate.breakdown.output_cost == pytest.approx(0.01)
    assert estimate.estimated_cost == pytest.approx(0.01125)
