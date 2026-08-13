"""Unit tests for OutputPIIModule — post-execution PII scanning."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "src"))

import pytest

from tealtiger.pipeline.modules.post.output_pii import OutputPIIModule


@pytest.mark.asyncio
class TestOutputPIIModuleIBAN:
    async def test_deny_on_iban_in_response(self):
        module = OutputPIIModule()
        request = {"_response": "Sure, the IBAN is GB29 NWBK 6016 1331 9268 19"}
        result = await module.evaluate(request, ctx={}, policy={})
        assert result["action"] == "DENY"
        assert "PII_IN_RESPONSE" in result["reason_codes"]
        patterns = [f["pattern"] for f in result["metadata"]["findings"]]
        assert "iban" in patterns

    async def test_allow_on_clean_response(self):
        module = OutputPIIModule()
        request = {"_response": "The weather today is sunny."}
        result = await module.evaluate(request, ctx={}, policy={})
        assert result["action"] == "ALLOW"


@pytest.mark.asyncio
class TestOutputPIIModulePassport:
    async def test_deny_on_passport_in_response(self):
        module = OutputPIIModule()
        request = {"_response": "Your passport number is A12345678"}
        result = await module.evaluate(request, ctx={}, policy={})
        assert result["action"] == "DENY"
        patterns = [f["pattern"] for f in result["metadata"]["findings"]]
        assert "passport" in patterns
