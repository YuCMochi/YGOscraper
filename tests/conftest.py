"""
tests/conftest.py - 共用 fixtures
"""
import json
import shutil
import tempfile
from pathlib import Path

import pytest

# Fixtures 檔案目錄
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def tmp_dir():
    """提供一個臨時目錄，測試結束後自動清除。"""
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d)


@pytest.fixture
def sample_cart_data():
    """讀取 fixtures/sample_cart.json 並回傳 dict。"""
    with open(FIXTURES_DIR / "sample_cart.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def sample_cart_path():
    """回傳 fixtures/sample_cart.json 的路徑字串。"""
    return str(FIXTURES_DIR / "sample_cart.json")


@pytest.fixture
def sample_ruten_csv_path():
    """回傳 fixtures/sample_ruten_data.csv 的路徑字串。"""
    return str(FIXTURES_DIR / "sample_ruten_data.csv")
