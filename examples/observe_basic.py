"""Basic observe() demo for TealTiger.
Uses a mock OpenAI client so you can run this without an API key.
Shows cost tracking and the freeze()/unfreeze() kill switch.
"""

from tealtiger.observe import FrozenAgentError, freeze, observe, unfreeze


# Mock classes for OpenAI client response, to avoid actual API calls.
class MockUsage:
    """Mock usage object matching OpenAI response.usage schema."""

    def __init__(self, prompt_tokens=10, completion_tokens=20, total_tokens=30):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class MockMessage:
    """Mock message in a chat completion choice."""

    def __init__(self, content="Hello!", tool_calls=None):
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


def main():
    # Wrap the client — drop-in proxy; call it like a normal OpenAI client
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


if __name__ == "__main__":
    main()
