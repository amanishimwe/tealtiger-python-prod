"""Basic observe() demo for TealTiger.
Uses a mock OpenAI client so you can run this without an API key.
Shows cost tracking and the freeze()/unfreeze() kill switch.
"""

from tealtiger.observe import FrozenAgentError, freeze, observe, unfreeze


# =======================================================================
# for OpenAI
# =======================================================================
# Mock classes for OpenAI client response, to avoid actual API calls.
class MockUsage:
    """Mock usage object matching OpenAI response.usage schema."""

    def __init__(self, prompt_tokens=10, completion_tokens=20, total_tokens=30):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class MockMessage:
    """Mock message in a chat completion choice."""

    def __init__(self, content="Hello from mock OpenAI!", tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls


class MockChoice:
    """Mock choice in a chat completion response."""

    def __init__(self, message=None):
        self.message = message or MockMessage()


class MockOpenAIResponse:
    """Mock OpenAI response."""

    def __init__(self, model="gpt-4o", usage=None, choices=None):
        self.model = model
        self.usage = usage or MockUsage()
        self.choices = choices or [MockChoice()]


class MockCompletions:
    """Mock completions object."""

    def create(self, **kwargs):
        return MockOpenAIResponse()


class MockChat:
    """Mock chat object."""

    def __init__(self):
        self.completions = MockCompletions()


class MockOpenAI:
    """Mock OpenAI client."""

    def __init__(self):
        self.chat = MockChat()
        self.base_url = "https://api.openai.com/v1"


# ======================================================================
# for Anthropic
# ======================================================================


class MockAnthropicUsage:
    """Mock Anthropic usage object."""

    def __init__(self, input_tokens=15, output_tokens=25):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class MockMessages:
    """Mock Anthropic messages namespace."""

    def create(self, **kwargs):
        return MockAnthropicResponse()


class MockAnthropic:
    """Mock Anthropic client matching detection heuristics."""

    def __init__(self, input_tokens=15, output_tokens=25):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.messages = MockMessages()
        self.base_url = "https://api.anthropic.com"


class MockAnthropicResponse:
    """Mock Anthropic messages.create response."""

    def __init__(self):
        self.model = "claude-3-sonnet-20240229"
        self.usage = MockAnthropicUsage()
        self.content = "Hello from mock Anthropic!"
        self.stop_reason = "end_turn"


def demo_openai():
    # Wrap the client — drop-in proxy; call it like a normal OpenAI client
    print("=== OpenAI observe() demo ===\n")
    client = observe(MockOpenAI(), agent_id="demo-agent")
    # 1) Normal API request
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response.choices[0].message.content)
    print(client.get_cost())
    # 2) Kill switch: freeze blocks further calls for the agent
    freeze("demo-agent")
    try:
        client.chat.completions.create(model="gpt-4o", messages=[])
    except FrozenAgentError as e:
        print("blocked:", e)
    # 3) Unfreeze restores normal operation
    unfreeze("demo-agent")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Back online"}],
    )
    print(response.choices[0].message.content)


def demo_anthropic():
    print("\n=== Anthropic observe() demo ===\n")
    client = observe(MockAnthropic(), agent_id="demo-anthropic-agent")
    response = client.messages.create(
        model="claude-3-sonnet",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response.content)
    print(client.get_cost())
    freeze("demo-anthropic-agent")
    try:
        client.messages.create(model="claude-3-sonnet", messages=[])
    except FrozenAgentError as e:
        print("blocked:", e)
    unfreeze("demo-anthropic-agent")
    response = client.messages.create(
        model="claude-3-sonnet",
        messages=[{"role": "user", "content": "Back online"}],
    )
    print(response.content)


if __name__ == "__main__":
    demo_openai()
    demo_anthropic()
