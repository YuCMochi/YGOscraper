"""
tests/unit/test_calculator.py - PurchaseOptimizer unit tests

Tests call _solve() directly with in-memory data to avoid external I/O.
Output files (log + JSON) are written to a tmp_dir fixture.
"""
import pytest

from app.services.calculator_service import PurchaseOptimizer


def _make_listing(product_id, card_name, seller_id, price, stock):
    return {
        "listing_id": product_id,
        "search_card_name": card_name,
        "seller_id": seller_id,
        "price": price,
        "stock_qty": stock,
        "product_id": str(product_id),
        "product_name": f"{card_name} item",
        "post_time": "2024-01-01",
        "image_url": "",
    }


@pytest.fixture
def optimizer():
    return PurchaseOptimizer()


class TestSingleSellerOptimal:
    def test_single_seller_best_solution(self, optimizer, tmp_dir):
        """4.1 市場只有一個賣家且庫存足夠時，結果只使用該賣家"""
        data = [_make_listing(0, "青眼白龍", "seller_A", 200, 3)]
        needed = {"青眼白龍": 1}
        log_path = str(tmp_dir / "test.log")
        json_path = str(tmp_dir / "result.json")

        result = optimizer._solve(data, needed, 60, 0, log_path, json_path)

        assert "seller_A" in result["sellers"]
        assert result["summary"]["sellers_count"] == 1
        assert result["summary"]["grand_total"] == 200 + 60  # price + 1 shipping


class TestMultiSellerOptimal:
    def test_multi_seller_best_solution(self, optimizer, tmp_dir):
        """4.2 多賣家：選出含運費的最低組合"""
        # seller_A: 青眼白龍 500元, seller_B: 青眼白龍 100元
        # 兩家都需運費60元，所以 seller_B 總價 160 < seller_A 總價 560
        data = [
            _make_listing(0, "青眼白龍", "seller_A", 500, 5),
            _make_listing(1, "青眼白龍", "seller_B", 100, 5),
        ]
        needed = {"青眼白龍": 1}
        log_path = str(tmp_dir / "test.log")
        json_path = str(tmp_dir / "result.json")

        result = optimizer._solve(data, needed, 60, 0, log_path, json_path)

        assert "seller_B" in result["sellers"]
        assert "seller_A" not in result["sellers"]
        assert result["summary"]["grand_total"] == 100 + 60

    def test_cross_seller_is_cheaper(self, optimizer, tmp_dir):
        """4.2 跨賣家組合更便宜時選跨賣家"""
        # 青眼白龍只有 seller_A 有（200元）
        # 黑魔術師只有 seller_B 有（100元）
        # 兩家各一運費：60 * 2 = 120
        data = [
            _make_listing(0, "青眼白龍", "seller_A", 200, 1),
            _make_listing(1, "黑魔術師", "seller_B", 100, 1),
        ]
        needed = {"青眼白龍": 1, "黑魔術師": 1}
        log_path = str(tmp_dir / "test.log")
        json_path = str(tmp_dir / "result.json")

        result = optimizer._solve(data, needed, 60, 0, log_path, json_path)

        assert result["summary"]["sellers_count"] == 2
        assert result["summary"]["grand_total"] == 200 + 100 + 60 * 2


class TestInsufficientStock:
    def test_insufficient_stock_raises_runtime_error(self, optimizer, tmp_dir):
        """4.3 庫存不足時拋出 RuntimeError"""
        data = [_make_listing(0, "青眼白龍", "seller_A", 200, 1)]
        needed = {"青眼白龍": 3}  # 需要3張，但只有1張庫存
        log_path = str(tmp_dir / "test.log")
        json_path = str(tmp_dir / "result.json")

        with pytest.raises(RuntimeError, match="庫存"):
            optimizer._solve(data, needed, 60, 0, log_path, json_path)


class TestMinPurchaseLimit:
    def test_min_purchase_limit_respected(self, optimizer, tmp_dir):
        """4.4 設定最低消費門檻時，每個選中的賣家都達到門檻"""
        # seller_A: 青眼白龍 50元（低於 min_purchase 100）
        # seller_B: 青眼白龍 150元（高於 min_purchase 100）
        # 在 min_purchase=100 的情況下，solver 只能選 seller_B
        data = [
            _make_listing(0, "青眼白龍", "seller_A", 50, 5),
            _make_listing(1, "青眼白龍", "seller_B", 150, 5),
        ]
        needed = {"青眼白龍": 1}
        log_path = str(tmp_dir / "test.log")
        json_path = str(tmp_dir / "result.json")

        result = optimizer._solve(data, needed, 60, 100, log_path, json_path)

        # 因為最低消費100，seller_A(50元) 不符合 → 選 seller_B
        assert "seller_B" in result["sellers"]
        assert "seller_A" not in result["sellers"]
