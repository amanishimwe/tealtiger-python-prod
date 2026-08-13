"""Unit tests for TealTigerCallback — Google ADK pii_block policy."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from tealtiger.integrations.google_adk import TealTigerCallback


class TestPiiBlockPolicyIBAN:
    def test_before_tool_denies_on_iban(self):
        callback = TealTigerCallback(
            policies=[{"type": "pii_block", "categories": ["iban"]}],
            mode="ENFORCE",
        )
        result = callback.before_tool(
            callback_context=None,
            tool="send_message",
            args={"text": "Wire to GB29 NWBK 6016 1331 9268 19"},
        )
        assert result is not None
        assert "GOVERNANCE DENIED" in result["content"]
        assert callback.deny_count == 1

    def test_before_tool_allows_clean_content(self):
        callback = TealTigerCallback(
            policies=[{"type": "pii_block", "categories": ["iban"]}],
            mode="ENFORCE",
        )
        result = callback.before_tool(
            callback_context=None,
            tool="send_message",
            args={"text": "Hello there"},
        )
        assert result is None


class TestPiiBlockPolicyPassport:
    def test_before_tool_denies_on_us_passport(self):
        callback = TealTigerCallback(
            policies=[{"type": "pii_block", "categories": ["passport"]}],
            mode="ENFORCE",
        )
        result = callback.before_tool(
            callback_context=None,
            tool="send_message",
            args={"text": "Passport A12345678"},
        )
        assert result is not None
        assert callback.deny_count == 1

    def test_before_tool_denies_on_india_passport(self):
        callback = TealTigerCallback(
            policies=[{"type": "pii_block", "categories": ["passport"]}],
            mode="ENFORCE",
        )
        result = callback.before_tool(
            callback_context=None,
            tool="send_message",
            args={"text": "Passport 123456789"},
        )
        assert result is not None
        assert callback.deny_count == 1
