"""
Unit tests for ObservePIIScanner — REPORT_ONLY mode PII detection.

Follows the module import path setup used in
tests/observe/test_observe_governance.py.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


from tealtiger.observe.pii_scanner import ObservePIIScanner


class TestObservePIIScannerExistingPatterns:
    """Sanity checks for pre-existing pattern types (regression guard)."""

    def test_scan_detects_email(self):
        scanner = ObservePIIScanner()
        result = scanner.scan("Contact: test@example.com", phase="request")
        assert result is not None
        assert "email" in result.types

    def test_scan_clean_text_returns_none(self):
        scanner = ObservePIIScanner()
        result = scanner.scan("Hello, how are you?", phase="request")
        assert result is None


class TestObservePIIScannerIBAN:
    """IBAN detection via ObservePIIScanner.scan()."""

    def test_scan_detects_iban_request_phase(self):
        scanner = ObservePIIScanner()
        result = scanner.scan(
            "IBAN: GB29 NWBK 6016 1331 9268 19", phase="request"
        )
        assert result is not None
        assert "iban" in result.types
        assert result.phase == "request"

    def test_scan_detects_iban_response_phase(self):
        scanner = ObservePIIScanner()
        result = scanner.scan(
            "Here is your IBAN: DE89 3704 0044 0532 0130 00", phase="response"
        )
        assert result is not None
        assert "iban" in result.types
        assert result.phase == "response"


class TestObservePIIScannerPassport:
    """Passport detection via ObservePIIScanner.scan()."""

    def test_scan_detects_us_passport(self):
        scanner = ObservePIIScanner()
        result = scanner.scan("Passport number: A12345678", phase="request")
        assert result is not None
        assert "passport" in result.types

    def test_scan_detects_india_passport(self):
        scanner = ObservePIIScanner()
        result = scanner.scan("Passport number: 123456789", phase="request")
        assert result is not None
        assert "passport" in result.types

    def test_scan_never_exposes_matched_values(self):
        """PIIDetectionSummary output must never contain raw matched values (Req 5.3)."""
        scanner = ObservePIIScanner()
        content = "Passport number: A12345678"
        result = scanner.scan(content, phase="request")
        assert not hasattr(result, "value")
        assert not hasattr(result, "values")
