import pytest
from tealtiger.integrations.google_adk import TealTigerCallback

def test_allow_tracks_cost():
    g = TealTigerCallback(cost_per_tool_call=0.01, mode="ENFORCE")
    result = g.before_tool(None, "search",{})
    assert result is None
    assert g.total_cost == 0.01
    assert g.decisions[0]["action"] == "ALLOW"
    assert g.decisions[0]["cumulative_cost"] == 0.01

def test_allowlist_deny_blocks_in_enforce_mode():
    g = TealTigerCallback(
        policies=[{"type": "tool_allowlist","allowed":["search"]}],
        mode="ENFORCE",
    )
    result = g.before_tool(None, "delete_all",{})
    assert result is not None
    assert "content" in result
    assert g.decisions[0]["action"] == "DENY"
    assert g.total_cost == 0.0

def test_freeze_deni():
    g = TealTigerCallback(mode="ENFORCE")
    g.freeze()
    result  = g.before_tool(None,"search", {})
    assert result is not None
    assert "AGENT_FROZEN" in g.decisions[0]["reason_codes"]
    assert g.total_cost == 0.0