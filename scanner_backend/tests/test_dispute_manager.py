from dispute_manager import DisputeManager, DisputeStatus, ManagedDispute, make_mock_bureau_json


def test_audit_tradeline_flags_50_mock_contradictions():
    manager = DisputeManager()
    results = [manager.audit_tradeline(make_mock_bureau_json(i)) for i in range(50)]

    assert all(result["has_contradictions"] for result in results)
    assert all(result["flag_count"] >= 3 for result in results)
    assert all(
        {"balance_mismatch", "dofd_mismatch", "status_mismatch"}.issubset(
            {flag["type"] for flag in result["flags"]}
        )
        for result in results
    )


def test_verified_response_escalates_to_mov_with_retention_message():
    manager = DisputeManager()
    dispute = ManagedDispute(id=1)

    updated = manager.transition_state(dispute, "verified")

    assert updated.status == DisputeStatus.ESCALATED_MOV
    assert updated.history_log[-1]["strategy"] == "Data Hygiene"
    assert "Strategy B" in updated.history_log[-1]["customer_message"]


def test_history_summary_template_injects_round_history():
    manager = DisputeManager()
    dispute = ManagedDispute(id=2)
    for response in ["verified", "no_response", "verified", "verified"]:
        manager.transition_state(dispute, response)

    letter = manager.generate_history_summary_header(
        dispute,
        bureau_name="Experian",
        account_number="****1234",
    )

    assert "TO: Experian" in letter
    assert "ACCOUNT #****1234" in letter
    assert "I have disputed this item 4 times" in letter
    assert "Strategy Forensic Audit" in letter
    assert "FCRA 611(a)(7)" in letter
