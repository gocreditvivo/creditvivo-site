from report_ingestion import (
    build_extracted_text_ingestion,
    build_parser_json_ingestion,
    build_structured_report_ingestion,
    build_uploaded_pdf_ingestion,
    normalize_ingestion_items,
)


def test_uploaded_pdf_ingestion_keeps_native_parser_default():
    item = build_uploaded_pdf_ingestion(
        source_filename="experian.pdf",
        text="--- PAGE 1 ---\nExperian Credit Report",
        bureau="Experian",
        pages=1,
    )
    report_texts = normalize_ingestion_items([item])

    assert report_texts["experian.pdf"]["text"].startswith("--- PAGE 1 ---")
    assert report_texts["experian.pdf"]["bureau"] == "Experian"
    assert report_texts["experian.pdf"]["ingestion_source"] == "uploaded_pdf_native_text"
    assert report_texts["experian.pdf"]["parser_name"] == "credit_vivo_native_pdf"
    assert report_texts["experian.pdf"]["consumer_report_only"] is True
    assert report_texts["experian.pdf"]["metadata"]["default_parser"] is True


def test_ingestion_rejects_non_consumer_report_domain():
    try:
        build_extracted_text_ingestion(
            source_filename="business-report.txt",
            text="commercial report",
            report_domain="commercial_credit_report",
        )
    except ValueError as exc:
        assert "consumer credit reports only" in str(exc)
    else:
        raise AssertionError("commercial report ingestion should be rejected")


def test_reserved_future_inputs_normalize_without_vendor_integration():
    parser_item = build_parser_json_ingestion(
        source_filename="parser.json",
        parser_payload={"raw_text": "Equifax Credit Report"},
        bureau="Equifax",
    )
    structured_item = build_structured_report_ingestion(
        source_filename="bureau-api.json",
        structured_payload={"tradelines": []},
        bureau="TransUnion",
    )

    report_texts = normalize_ingestion_items([parser_item, structured_item])

    assert report_texts["parser.json"]["ingestion_source"] == "third_party_parser_json"
    assert report_texts["parser.json"]["metadata"]["adapter_status"] == "reserved_not_integrated"
    assert report_texts["bureau-api.json"]["ingestion_source"] == "structured_bureau_api"
    assert report_texts["bureau-api.json"]["parser_name"] == "reserved_structured_report_adapter"

