from __future__ import annotations

"""
Credit Vivo Report Ingestion Layer v18 foundation.

This module keeps uploaded consumer PDF reports on the native Credit Vivo parser
path while defining a narrow normalization contract for future text, parser JSON,
or structured bureau/API inputs.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Literal


CONSUMER_REPORT_DOMAIN = "consumer_credit_report"
NATIVE_PDF_SOURCE = "uploaded_pdf_native_text"

ReportSourceType = Literal[
    "uploaded_pdf_native_text",
    "extracted_text",
    "third_party_parser_json",
    "structured_bureau_api",
]


@dataclass
class ReportIngestionItem:
    source_filename: str
    text: str
    bureau: str
    source_type: ReportSourceType = NATIVE_PDF_SOURCE
    report_domain: str = CONSUMER_REPORT_DOMAIN
    parser_name: str = "credit_vivo_native_pdf"
    metadata: Dict[str, Any] = field(default_factory=dict)
    structured_payload: Dict[str, Any] = field(default_factory=dict)


def _require_consumer_report(report_domain: str) -> None:
    if report_domain != CONSUMER_REPORT_DOMAIN:
        raise ValueError("Credit Vivo scanner accepts consumer credit reports only.")


def build_uploaded_pdf_ingestion(
    *,
    source_filename: str,
    text: str,
    bureau: str,
    pages: int = 0,
    chars: int | None = None,
) -> ReportIngestionItem:
    return ReportIngestionItem(
        source_filename=source_filename,
        text=text,
        bureau=bureau,
        source_type=NATIVE_PDF_SOURCE,
        parser_name="credit_vivo_native_pdf",
        metadata={
            "pages": pages,
            "chars": len(text) if chars is None else chars,
            "default_parser": True,
        },
    )


def build_extracted_text_ingestion(
    *,
    source_filename: str,
    text: str,
    bureau: str = "Unknown Bureau",
    report_domain: str = CONSUMER_REPORT_DOMAIN,
) -> ReportIngestionItem:
    _require_consumer_report(report_domain)
    return ReportIngestionItem(
        source_filename=source_filename,
        text=text,
        bureau=bureau,
        source_type="extracted_text",
        parser_name="external_text_source",
    )


def build_parser_json_ingestion(
    *,
    source_filename: str,
    parser_payload: Dict[str, Any],
    bureau: str = "Unknown Bureau",
    parser_name: str = "reserved_parser_json_adapter",
    report_domain: str = CONSUMER_REPORT_DOMAIN,
) -> ReportIngestionItem:
    _require_consumer_report(report_domain)
    text = str(
        parser_payload.get("raw_text")
        or parser_payload.get("extracted_text")
        or parser_payload.get("text")
        or ""
    )
    return ReportIngestionItem(
        source_filename=source_filename,
        text=text,
        bureau=bureau,
        source_type="third_party_parser_json",
        parser_name=parser_name,
        metadata={"adapter_status": "reserved_not_integrated"},
        structured_payload=parser_payload,
    )


def build_structured_report_ingestion(
    *,
    source_filename: str,
    structured_payload: Dict[str, Any],
    bureau: str = "Unknown Bureau",
    source_name: str = "reserved_structured_report_adapter",
    report_domain: str = CONSUMER_REPORT_DOMAIN,
) -> ReportIngestionItem:
    _require_consumer_report(report_domain)
    text = str(structured_payload.get("raw_text") or "")
    return ReportIngestionItem(
        source_filename=source_filename,
        text=text,
        bureau=bureau,
        source_type="structured_bureau_api",
        parser_name=source_name,
        metadata={"adapter_status": "reserved_not_integrated"},
        structured_payload=structured_payload,
    )


def normalize_ingestion_items(items: Iterable[ReportIngestionItem]) -> Dict[str, dict]:
    report_texts: Dict[str, dict] = {}
    for item in items:
        _require_consumer_report(item.report_domain)
        report_texts[item.source_filename] = {
            "text": item.text,
            "bureau": item.bureau,
            "ingestion_source": item.source_type,
            "parser_name": item.parser_name,
            "consumer_report_only": True,
            "metadata": item.metadata,
            "structured_payload": item.structured_payload,
        }
    return report_texts

