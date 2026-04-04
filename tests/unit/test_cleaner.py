"""
tests/unit/test_cleaner.py - DataCleaner unit tests

DataCleaner.clean() reads files directly, so we write temp files
to avoid touching real data/ directories.
"""
import csv
import json
import os

import pytest

from app.services.cleaner_service import DataCleaner


def _write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_cart(path: str, cart: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cart, f)


def _read_output(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


FIELDNAMES = [
    "product_id", "search_card_name", "product_name", "seller_id",
    "price", "stock_qty", "alt_price", "image_url", "post_time", "shipping_cost",
]

BASE_CART = {
    "shopping_cart": [
        {
            "card_name_zh": "青眼白龍",
            "required_amount": 1,
            "target_card_numbers": ["SDK-001"],
        }
    ],
    "global_settings": {
        "default_shipping_cost": 60,
        "min_purchase_limit": 0,
        "global_exclude_keywords": [],
        "global_exclude_seller": [],
    },
    "cart_settings": {
        "shipping_cost": None,
        "min_purchase": None,
        "exclude_keywords": [],
        "exclude_seller": [],
    },
}

GOOD_ROW = {
    "product_id": "P001",
    "search_card_name": "青眼白龍",
    "product_name": "SDK-001 青眼白龍",
    "seller_id": "seller_A",
    "price": "200",
    "stock_qty": "3",
    "alt_price": "0",
    "image_url": "https://gcs.rimg.com.tw/img001.jpg",
    "post_time": "2024-01-01",
    "shipping_cost": "60",
}


@pytest.fixture
def setup(tmp_dir):
    input_csv = str(tmp_dir / "input.csv")
    output_csv = str(tmp_dir / "output.csv")
    cart_path = str(tmp_dir / "cart.json")
    return input_csv, output_csv, cart_path


def test_blacklist_seller_filtered(setup):
    """3.1 黑名單賣家的商品被過濾掉"""
    input_csv, output_csv, cart_path = setup

    cart = {**BASE_CART}
    cart["global_settings"] = {**BASE_CART["global_settings"], "global_exclude_seller": ["bad_seller"]}
    _write_cart(cart_path, cart)

    rows = [
        GOOD_ROW,
        {**GOOD_ROW, "product_id": "P002", "seller_id": "bad_seller"},
    ]
    _write_csv(input_csv, rows, FIELDNAMES)

    DataCleaner().clean(input_csv, output_csv, cart_path)
    result = _read_output(output_csv)

    assert len(result) == 1
    assert result[0]["seller_id"] == "seller_A"


def test_price_over_5000_filtered(setup):
    """3.2 價格超過 5000 的商品被過濾掉"""
    input_csv, output_csv, cart_path = setup
    _write_cart(cart_path, BASE_CART)

    rows = [
        GOOD_ROW,
        {**GOOD_ROW, "product_id": "P002", "price": "5001"},
    ]
    _write_csv(input_csv, rows, FIELDNAMES)

    DataCleaner().clean(input_csv, output_csv, cart_path)
    result = _read_output(output_csv)

    assert len(result) == 1
    assert result[0]["price"] == "200"


def test_ebay_product_name_filtered(setup):
    """3.3 商品名稱含 ebay 的商品被過濾掉"""
    input_csv, output_csv, cart_path = setup
    _write_cart(cart_path, BASE_CART)

    rows = [
        GOOD_ROW,
        {**GOOD_ROW, "product_id": "P002", "product_name": "ebay SDK-001 青眼白龍"},
    ]
    _write_csv(input_csv, rows, FIELDNAMES)

    DataCleaner().clean(input_csv, output_csv, cart_path)
    result = _read_output(output_csv)

    assert len(result) == 1
    assert "ebay" not in result[0]["product_name"].lower()


def test_ebay_image_url_filtered(setup):
    """3.3 image_url 含 ebay 的商品被過濾掉"""
    input_csv, output_csv, cart_path = setup
    _write_cart(cart_path, BASE_CART)

    rows = [
        GOOD_ROW,
        {**GOOD_ROW, "product_id": "P002", "image_url": "https://i.ebay.com/img.jpg"},
    ]
    _write_csv(input_csv, rows, FIELDNAMES)

    DataCleaner().clean(input_csv, output_csv, cart_path)
    result = _read_output(output_csv)

    assert len(result) == 1


def test_exclude_keyword_filtered(setup):
    """3.4 商品名稱含排除關鍵字的商品被過濾掉"""
    input_csv, output_csv, cart_path = setup

    cart = {**BASE_CART}
    cart["global_settings"] = {**BASE_CART["global_settings"], "global_exclude_keywords": ["卡套"]}
    _write_cart(cart_path, cart)

    rows = [
        GOOD_ROW,
        {**GOOD_ROW, "product_id": "P002", "product_name": "SDK-001 卡套 青眼白龍"},
    ]
    _write_csv(input_csv, rows, FIELDNAMES)

    DataCleaner().clean(input_csv, output_csv, cart_path)
    result = _read_output(output_csv)

    assert len(result) == 1
    assert "卡套" not in result[0]["product_name"]


def test_card_number_exact_match(setup):
    """3.5 SD5 不應匹配 YSD5（精確卡號比對）"""
    input_csv, output_csv, cart_path = setup

    cart = {**BASE_CART}
    cart["shopping_cart"] = [
        {"card_name_zh": "青眼白龍", "required_amount": 1, "target_card_numbers": ["SD5"]}
    ]
    _write_cart(cart_path, cart)

    rows = [
        {**GOOD_ROW, "product_name": "SD5-JP001 青眼白龍"},
        {**GOOD_ROW, "product_id": "P002", "product_name": "YSD5-JP001 青眼白龍"},
    ]
    _write_csv(input_csv, rows, FIELDNAMES)

    DataCleaner().clean(input_csv, output_csv, cart_path)
    result = _read_output(output_csv)

    assert len(result) == 1
    assert "SD5-JP001" in result[0]["product_name"]
    assert "YSD5" not in result[0]["product_name"]


def test_duplicate_product_id_deduplicated(setup):
    """3.6 相同 product_id 的重複列只保留第一筆"""
    input_csv, output_csv, cart_path = setup
    _write_cart(cart_path, BASE_CART)

    rows = [
        GOOD_ROW,
        {**GOOD_ROW, "seller_id": "seller_B"},  # 同 product_id P001
    ]
    _write_csv(input_csv, rows, FIELDNAMES)

    DataCleaner().clean(input_csv, output_csv, cart_path)
    result = _read_output(output_csv)

    assert len(result) == 1
    assert result[0]["seller_id"] == "seller_A"
