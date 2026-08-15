import json
from pathlib import Path

import pytest

from credit_vivo_proprietary_engine import parse_reports, result_to_dict


GOLDEN_ROOT = Path(__file__).parent / "golden"
MANIFEST = json.loads((GOLDEN_ROOT / "manifest.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("fixture", MANIFEST["fixtures"], ids=lambda fixture: fixture["name"])
def test_golden_fixture_matches_expected_normalized_output(fixture):
    reports = {
        filename: {"text": (GOLDEN_ROOT / filename).read_text(encoding="utf-8")}
        for filename in fixture["files"]
    }
    first = result_to_dict(parse_reports(reports))
    second = result_to_dict(parse_reports(reports))

    # Parser output must be deterministic for the same versioned fixture.
    assert first == second
    projected = [
        {
            "bureau": row["bureau"],
            "account": row["account_number_masked"],
            "name": row["account_name"],
            "type": row["account_type"],
            "status": row["status"],
            "balance": row["balance"],
        }
        for row in first["tradelines"]
    ]
    assert projected == fixture["tradelines"]
    assert sorted(row["issue_type"] for row in first["issues"]) == sorted(fixture["issue_types"])

    serialized = json.dumps(first, ensure_ascii=False)
    assert "100000000001" not in serialized
    assert "200000000002" not in serialized
    assert "300000000003" not in serialized
    assert "400000000004" not in serialized
    assert "500000000005" not in serialized
    assert "600000000006" not in serialized
    assert "700000000007" not in serialized
    assert "800000000008" not in serialized
