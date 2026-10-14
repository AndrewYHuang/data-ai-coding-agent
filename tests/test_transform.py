"""Tests for the helper functions Andy never finished (exercise 02).

These fail until the helpers in kettle/transform.py are implemented.
Do not change these tests to make them pass - change the code.
"""

import json
from datetime import datetime

import pytest

from kettle.transform import (
    format_pence,
    normalise_product_name,
    parse_price_to_pence,
    parse_till_timestamp,
)

with open("data/reference/products.json", encoding="utf-8") as f:
    PRODUCTS = json.load(f)


# --- format_pence -------------------------------------------------------------


@pytest.mark.parametrize(
    "pence, expected",
    [
        (340, "£3.40"),
        (0, "£0.00"),
        (5, "£0.05"),
        (1000, "£10.00"),
        (123456, "£1234.56"),
        (-120, "-£1.20"),
    ],
)
def test_format_pence(pence, expected):
    assert format_pence(pence) == expected


# --- parse_price_to_pence -----------------------------------------------------


@pytest.mark.parametrize(
    "value, unit, expected",
    [
        ("3.40", "pounds", 340),
        ("3.4", "pounds", 340),
        ("3", "pounds", 300),
        (" 2.60 ", "pounds", 260),
        ("4.35", "pounds", 435),
        ("0.29", "pounds", 29),
        ("340", "pence", 340),
        (" 220", "pence", 220),
    ],
)
def test_parse_price_to_pence(value, unit, expected):
    assert parse_price_to_pence(value, unit) == expected


@pytest.mark.parametrize(
    "value, unit",
    [
        ("N/A", "pounds"),
        ("", "pounds"),
        ("3.405", "pounds"),
        ("340.5", "pence"),
        ("abc", "pence"),
    ],
)
def test_parse_price_to_pence_rejects_bad_values(value, unit):
    with pytest.raises(ValueError):
        parse_price_to_pence(value, unit)


# --- parse_till_timestamp -----------------------------------------------------


@pytest.mark.parametrize(
    "value, expected",
    [
        ("14/09/2026 08:15", datetime(2026, 9, 14, 8, 15)),
        ("01/02/2026 09:00", datetime(2026, 2, 1, 9, 0)),  # 1st Feb, not 2nd Jan
        ("2026-09-14T08:15:00", datetime(2026, 9, 14, 8, 15)),
        ("  2026-09-14T17:59:00 ", datetime(2026, 9, 14, 17, 59)),
    ],
)
def test_parse_till_timestamp(value, expected):
    assert parse_till_timestamp(value) == expected


@pytest.mark.parametrize("value", ["", "yesterday", "14/09/2026", "2026-13-01T00:00:00"])
def test_parse_till_timestamp_rejects_bad_values(value):
    with pytest.raises(ValueError):
        parse_till_timestamp(value)


# --- normalise_product_name ---------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Flat White", "Flat White"),
        ("FLAT WHITE", "Flat White"),
        ("flat-white", "Flat White"),
        (" Flat White ", "Flat White"),
        ("pain-au-chocolat", "Pain au Chocolat"),
        ("Pain Au Choc", "Pain au Chocolat"),
        ("Tea", "Breakfast Tea"),
        ("hot choc", "Hot Chocolate"),
    ],
)
def test_normalise_product_name(raw, expected):
    assert normalise_product_name(raw, PRODUCTS) == expected


@pytest.mark.parametrize("raw", ["", "   ", "Mocha", "Flat"])
def test_normalise_product_name_unknown(raw):
    assert normalise_product_name(raw, PRODUCTS) is None
