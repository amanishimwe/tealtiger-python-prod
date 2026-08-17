"""Example: TealTiger governance callbacks for Google ADK.
Calls before_tool / after_tool with mocks — no API key or google-adk required.
Run:
    python examples/google_adk_governance.py
"""

from tealtiger.integrations import TealTigerCallback


def main():
    governance = TealTigerCallback(
        policies=[
            {"type": "tool_allowlist", "allowed": ["search", "lookup*"]},
            {"type": "pii_block", "categories": ["ssn", "email"]},
            {"type": "cost_limit", "max_per_session": 0.05},
        ],
        mode="ENFORCE",
        model="gemini-2.5-flash",
        cost_per_tool_call=0.01,
        agent_id="demo-adk-agent",
    )
    print("=== 1) ALLOW: search ===")
    result = governance.before_tool(None, "search", {"query": "weather"})
    print("block result:", result)  # None = allowed
    governance.after_tool(None, "search", {"query": "weather"}, result="ok")
    print("cost:", governance.total_cost)
    print("decision:", governance.decisions[-1]["action"], governance.decisions[-1]["reason_codes"])
    print("\n=== 2) DENY: tool not allowlisted ===")
    result = governance.before_tool(None, "delete_all", {})
    print("block result:", result)  # dict with content
    print("deny_count:", governance.deny_count)
    print("\n=== 3) DENY: PII in args ===")
    result = governance.before_tool(
        None,
        "search",
        {"note": "ssn 123-45-6789"},
    )
    print("block result:", result)
    print("\n=== 4) freeze / unfreeze ===")
    governance.freeze()
    result = governance.before_tool(None, "search", {"query": "x"})
    print("frozen block:", result)  # dict — blocked while frozen
    governance.unfreeze()
    result = governance.before_tool(None, "search", {"query": "x"})
    print("after unfreeze:", result)  # None — allowed again
    print("\n=== summary ===")
    print("total_cost:", governance.total_cost)
    print("decisions:", len(governance.decisions))
    print("denies:", governance.deny_count)


if __name__ == "__main__":
    main()
