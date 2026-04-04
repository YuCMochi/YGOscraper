"""
tests/unit/test_schemas.py - Pydantic schema unit tests
"""
import pytest
from pydantic import ValidationError

from app.schemas import CartData, CartItemFull


class TestCartItemFull:
    def test_valid_data(self):
        """2.1 CartItemFull 接受合法資料"""
        item = CartItemFull(card_name_zh="青眼白龍", required_amount=2)
        assert item.card_name_zh == "青眼白龍"
        assert item.required_amount == 2

    def test_valid_with_optional_fields(self):
        item = CartItemFull(
            card_name_zh="黑魔術師",
            required_amount=1,
            passcode="89631139",
            cid=12345,
            target_card_numbers=["SDY-006"],
        )
        assert item.passcode == "89631139"
        assert item.cid == 12345

    def test_rejects_zero_required_amount(self):
        """2.2 CartItemFull 拒絕 required_amount = 0"""
        with pytest.raises(ValidationError):
            CartItemFull(card_name_zh="青眼白龍", required_amount=0)

    def test_rejects_negative_required_amount(self):
        """2.2 CartItemFull 拒絕 required_amount < 0"""
        with pytest.raises(ValidationError):
            CartItemFull(card_name_zh="青眼白龍", required_amount=-1)

    def test_def_alias(self):
        """def_ 欄位可用 'def' alias 傳入"""
        item = CartItemFull(card_name_zh="Test", required_amount=1, **{"def": 2000})
        assert item.def_ == 2000


class TestCartData:
    def test_default_values(self):
        """2.3 CartData 只傳 shopping_cart 時使用預設值"""
        cart = CartData(shopping_cart=[])
        assert cart.global_settings.default_shipping_cost == 60
        assert cart.global_settings.min_purchase_limit == 0
        assert cart.global_settings.global_exclude_keywords == []
        assert cart.global_settings.global_exclude_seller == []

    def test_empty_cart_settings_defaults(self):
        cart = CartData(shopping_cart=[])
        assert cart.cart_settings.shipping_cost is None
        assert cart.cart_settings.min_purchase is None
