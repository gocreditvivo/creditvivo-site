import json

from credit_vivo_native_parser import parse_credit_reports


def test_native_match_notes_use_the_central_output_sanitizer():
    separated_identifier = "9876-5432-1012-3456"
    report = f"""Experian Credit Report
SYNTHETIC BANK {separated_identifier}
Account Number: 1234567890
Account Type: Collection
Balance: $20
Status: Collection
"""
    result = parse_credit_reports({"Experian": report, "Equifax": report.replace("Experian", "Equifax")})
    serialized = json.dumps(result)
    assert separated_identifier not in serialized
    assert separated_identifier.replace("-", "") not in serialized
    assert f"syntheticref{separated_identifier.replace('-', '')}" not in serialized.lower()
    assert "1234567890" not in serialized
    assert result["bureau_match_notes"][0]["group"].startswith("match_")
