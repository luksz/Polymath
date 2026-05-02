from dataclasses import dataclass


@dataclass
class ModelPricing:
    input_per_1k: int    # micro-USD per 1000 input tokens
    output_per_1k: int   # micro-USD per 1000 output tokens


# Pricing table — update quarterly. All values in micro-USD per 1000 tokens.
PRICING: dict[str, ModelPricing] = {
    # Anthropic Claude 4.x
    "claude-opus-4-7": ModelPricing(input_per_1k=15_000, output_per_1k=75_000),
    "claude-sonnet-4-6": ModelPricing(input_per_1k=3_000, output_per_1k=15_000),
    "claude-haiku-4-5-20251001": ModelPricing(input_per_1k=250, output_per_1k=1_250),
    # OpenAI
    "gpt-4o": ModelPricing(input_per_1k=5_000, output_per_1k=15_000),
    "gpt-4o-mini": ModelPricing(input_per_1k=150, output_per_1k=600),
    "gpt-4-turbo": ModelPricing(input_per_1k=10_000, output_per_1k=30_000),
    # Embeddings
    "text-embedding-3-small": ModelPricing(input_per_1k=20, output_per_1k=0),
    "text-embedding-3-large": ModelPricing(input_per_1k=130, output_per_1k=0),
    "voyage-large-2": ModelPricing(input_per_1k=120, output_per_1k=0),
}


class CostCalculator:
    def calculate(self, model: str, input_tokens: int, output_tokens: int) -> int:
        """Return cost in micro-USD. Returns 0 if model is unknown."""
        pricing = PRICING.get(model)
        if not pricing:
            return 0
        input_cost = (input_tokens * pricing.input_per_1k) // 1000
        output_cost = (output_tokens * pricing.output_per_1k) // 1000
        return input_cost + output_cost

    def estimate(self, model: str, input_tokens: int, max_tokens: int) -> int:
        """Estimate worst-case cost for budget pre-check."""
        return self.calculate(model, input_tokens, max_tokens)
