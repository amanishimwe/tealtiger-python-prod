"""Basic observe() demo for TealTiger.

Uses mock OpenAI, Anthropic, Gemini, and Mistral clients so you can run
this without an API key. Shows cost tracking and freeze()/unfreeze().
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


# ======================================================================
# for Gemini
# ======================================================================


class MockGeminiUsageMetadata:
    """Mock Gemini usage_metadata (prompt/candidates token counts)."""

    def __init__(
        self,
        prompt_token_count=12,
        candidates_token_count=18,
        total_token_count=30,
    ):
        self.prompt_token_count = prompt_token_count
        self.candidates_token_count = candidates_token_count
        self.total_token_count = total_token_count


class MockGeminiResponse:
    """Mock Gemini generate_content response."""

    def __init__(self, text="Hello from mock Gemini!"):
        self.text = text
        self.usage_metadata = MockGeminiUsageMetadata()


class MockGemini:
    """Mock Gemini client matching detection heuristics (generate_content)."""

    def __init__(self):
        self.base_url = ""

    def generate_content(self, **kwargs):
        return MockGeminiResponse()


# ======================================================================
# for Mistral
# ======================================================================


class MockMistralUsage:
    """Mock Mistral usage (OpenAI-compatible token fields)."""

    def __init__(self, prompt_tokens=11, completion_tokens=22, total_tokens=33):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class MockMistralResponse:
    """Mock Mistral chat response."""

    def __init__(self, content="Hello from mock Mistral!"):
        self.model = "mistral-large-latest"
        self.usage = MockMistralUsage()
        self.choices = [MockChoice(MockMessage(content=content))]


class MockMistral:
    """Mock Mistral client: class name must contain 'mistral'; chat callable."""

    def __init__(self):
        self.base_url = "https://api.mistral.ai/v1"

    def chat(self, **kwargs):
        return MockMistralResponse()


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


def demo_gemini():
    print("\n=== Gemini observe() demo ===\n")
    client = observe(MockGemini(), agent_id="demo-gemini-agent")
    response = client.generate_content(
        model="gemini-2.0-flash",
        contents="Hello!",
    )
    print(response.text)
    print(client.get_cost())
    freeze("demo-gemini-agent")
    try:
        client.generate_content(model="gemini-2.0-flash", contents="")
    except FrozenAgentError as e:
        print("blocked:", e)
    unfreeze("demo-gemini-agent")
    response = client.generate_content(
        model="gemini-2.0-flash",
        contents="Back online",
    )
    print(response.text)


def demo_mistral():
    print("\n=== Mistral observe() demo ===\n")
    client = observe(MockMistral(), agent_id="demo-mistral-agent")
    response = client.chat(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response.choices[0].message.content)
    print(client.get_cost())
    freeze("demo-mistral-agent")
    try:
        client.chat(model="mistral-large-latest", messages=[])
    except FrozenAgentError as e:
        print("blocked:", e)
    unfreeze("demo-mistral-agent")
    response = client.chat(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "Back online"}],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    demo_openai()
    demo_anthropic()
    demo_gemini()
    demo_mistral()
