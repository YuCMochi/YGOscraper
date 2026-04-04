# External APIs & Data Sources

> YGOscraper 使用的外部 API 和資料來源參考，供 agent 開發時查閱。

---

## 露天拍賣 API

| API | URL | 用途 | 狀態 |
|-----|-----|------|------|
| 搜尋商品 | `https://rtapi.ruten.com.tw/api/search/v3/index.php/core/seller/{keyword}/...` | 目前 `ruten_scraper.py` 使用中 | ✅ 使用中 |
| 商品詳細 (simple) | `https://rapi.ruten.com.tw/api/items/v2/list?gno={item_id}&level=simple` | `deliver_way`、`seller_score`、`store_name` | 💡 v0.5.0 |
| 商品詳細 (detail) | `https://rapi.ruten.com.tw/api/items/v2/list?gno={item_id}&level=detail` | 複數選項商品的個別價格/庫存 | 💡 v0.5.0 |
| 賣家資訊 | `https://rapi.ruten.com.tw/api/users/v1/index.php/{seller_id}/storeinfo` | 賣家店名、信用、佈告欄 | 💡 v0.5.0 |

**備註**：
- items/v2 支援一次查詢複數商品（用 `&gno=` 串接），確切上限待驗證
- `deliver_way` 欄位包含各運送方式與對應運費（郵寄/超商/宅配）
- `seller_score` 可用於品質排序或過濾低評分賣家

---

## Konami 官方資料

| 用途 | URL | 使用位置 |
|------|-----|---------|
| 查卡（by CID） | `https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid={cid}` | `konami_scraper.py` |
| 卡片密碼→CID 對照表 | `https://github.com/salix5/heliosphere/blob/master/data/cid_table.json` | `app/services/card_db.py` |

---

## salix5 資料源

| 用途 | URL | 使用位置 |
|------|-----|---------|
| 卡片圖床 | `https://github.com/salix5/query-data/blob/gh-pages/pics/{卡片密碼}.jpg` | 前端卡圖顯示 |
| 核心卡片數據（CDB） | `https://github.com/salix5/cdb/blob/gh-pages/cards.cdb` | `app/services/card_db.py` |

---

## Neuron（v0.6.0）

| 用途 | URL / 說明 |
|------|-----------|
| 牌組代碼解析 | Neuron App 官方牌組分享功能產生的代碼格式（待研究） |

**備註**：v0.6.0 實作時需先研究 Neuron 牌組代碼的格式與解析方式。

---

## 集中管理位置

所有外部 URL 在後端統一管理於 `app/config.py`，避免 hardcoded 網址散落各處。
新增外部 URL 時應先在 `config.py` 定義常數，再於各 service 引用。