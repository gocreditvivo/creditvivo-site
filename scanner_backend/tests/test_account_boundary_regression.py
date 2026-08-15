"""Synthetic regression locks for adjacent-account isolation."""

from credit_vivo_proprietary_engine import parse_tradelines_for_bureau


def by_account(tradelines):
    return {item.account_number_masked: item for item in tradelines}


def negative_blob(tradeline):
    values = [tradeline.status, tradeline.pay_status, tradeline.negative_item_type]
    values.extend(tradeline.negative_signals)
    return " ".join(str(value or "") for value in values).lower()


def test_adjacent_collection_chargeoff_and_short_creditor_stay_isolated():
    sample = """Experian Credit Report
SYNTHETIC COLLECTION SERVICES
Account Number: 1234567890
Account Type: Collection
Balance: $1,234
Status: Collection
SYNTHETIC CARD BANK
Account Number: 999988881111
Account Type: Credit Card
Balance: $0
Status: Charge-off transferred or sold
AMEX
Account Number: 555544443333
Account Type: Credit Card
Balance: $250
Status: Open
"""
    tradelines = parse_tradelines_for_bureau("Experian", "synthetic-dense.txt", sample)
    accounts = by_account(tradelines)

    assert set(accounts) == {"*7890", "*1111", "*3333"}
    assert "charge" not in negative_blob(accounts["*7890"])
    assert "charge" in negative_blob(accounts["*1111"])
    assert accounts["*3333"].account_name == "AMEX"
    assert "charge" not in negative_blob(accounts["*3333"])


def test_category_subheaders_do_not_shift_creditor_names():
    sample = """TransUnion Credit Report
SYNTHETIC FUNDING
Collections
Account Number: 1212121234
Status: Collection
Balance: $410
SYNTHETIC BANK
Revolving
Account Number: 3434343478
Status: Charge-off transferred or sold
Balance: $0
"""
    tradelines = parse_tradelines_for_bureau("TransUnion", "synthetic-subheaders.txt", sample)
    accounts = by_account(tradelines)

    assert set(accounts) == {"*1234", "*3478"}
    assert accounts["*1234"].account_name == "SYNTHETIC FUNDING"
    assert accounts["*3478"].account_name == "SYNTHETIC BANK"
    assert "charge" not in negative_blob(accounts["*1234"])
    assert "charge" in negative_blob(accounts["*3478"])
