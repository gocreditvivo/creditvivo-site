import main


def test_cfpb_packet_dashboard_routes_load():
    credentials = main.ensure_local_admin_credentials()
    founder_session = main.create_admin_session(credentials["username"])
    responses = [
        main.scanner_upload_page(),
        main.findings_page(),
        main.findings_compare_page(),
        main.findings_letters_page(),
        main.dashboard_documents_page(),
        main.dashboard_letters_page(),
        main.admin_documents_page(cv_admin_session=founder_session),
        main.admin_letters_page(cv_admin_session=founder_session),
    ]
    for response in responses:
        text = response.body.decode("utf-8")
        assert response.status_code == 200
        assert "localStorage" not in text


def test_cfpb_packet_api_health_mentions_no_paid_ai():
    assert main.health()["paid_ai_used"] is False
