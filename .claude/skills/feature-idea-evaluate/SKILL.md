---
name: Feature Idea Evaluate
description: This skill should be used when evaluating "未開始" feature ideas from the Notion Feature idea database. Typically triggered by the feature-idea-triage skill, or when the user says "評估 idea"、"分析新功能"、"幫我看這個 idea 可不可行"。Fills in complexity/utility/fit scores and writes implementation analysis, then moves ideas to "待處理" or "廢棄".
version: 0.1.0
---

# Feature Idea Evaluate

評估「📥 未開始」區的 idea，補齊所有量表欄位，在 Notion 頁面內容中寫入分析，再移至「🧐 待處理」或「☠️ 廢棄」。

**所有動作在取得使用者確認後才執行。**

## 評估流程

### Step 1：讀取待評估 idea

從 triage 取得的已分類資料中，取出所有狀態為「📥 未開始」的 idea。若直接觸發本 skill，先執行 triage Step 1–2 收集資料。

對每一個 idea 逐一讀取：
- 用 `mcp__claude_ai_Notion__notion-fetch` 帶入 page_id，一次取得完整 properties 與頁面內容（不需要額外呼叫）

### Step 2：結合專案現況分析

評估前先理解專案背景。閱讀 `docs/DEVELOPMENT_PLAN.md` 了解：
- 目前版本進度（哪些版本已完成、哪些在計畫中）
- 現有技術棧（Python FastAPI 後端 + React 前端）
- 已存在的功能避免重複實作

同時掃描 `app/` 和 `frontend/src/` 確認現況。

### Step 3：評估每個 idea

對每個 idea 進行以下分析：

**可行性評估面向**
1. **技術可行性**：現有架構能否支撐？需要哪些新技術？有無已知技術限制？
2. **複雜度評估**：實作工時、涉及層面（前/後端/DB）、依賴關係
3. **產品價值**：對使用者的實際幫助、與 YGOscraper 核心功能的相關程度
4. **可拓展性**：這個功能能衍伸出哪些其他功能？

**評分規則**

| 欄位 | 低 | 中 | 高 |
|------|----|----|-----|
| 複雜度 | 👩‍💻（1–2天，單層） | 👩‍💻👩‍💻（1週，跨層） | 👩‍💻👩‍💻👩‍💻（2週+，系統性） |
| 實用程度 | 💪（錦上添花） | 💪💪（明顯改善體驗） | 💪💪💪（核心功能，少了很麻煩） |
| 想實作度 | 🔥（有空再說） | 🔥🔥（值得排進計劃） | 🔥🔥🔥（迫切想做） |
| 產品契合度 | ❤️（周邊功能） | ❤️❤️（相關功能） | ❤️❤️❤️（核心延伸） |

**移動判斷標準**
- → **🧐 待處理**：產品契合度 ≥ ❤️❤️，且實用程度 ≥ 💪💪，或想實作度 🔥🔥🔥
- → **☠️ 廢棄**：契合度 ❤️ 且實用程度 💪，或技術上有根本性障礙
- → **🧐 待處理（暫緩）**：值得做但超出當前能力範圍，先放待處理但不立即排程

**標籤填寫規則**

評估時一併決定標籤（`標籤` 為 multi_select，可多選）：

| 標籤 | 意義 | 選項 ID |
|------|------|---------|
| `前端` | 涉及 React / UI | `f89287ec-79af-41c5-8bb7-436934858400` |
| `後端` | 涉及 FastAPI / Python service | `979c1633-2658-490a-bef3-86b4a92cd75c` |
| `DB` | 涉及資料庫/資料儲存 | `4ee5137a-7453-4696-8181-424529ccf803` |
| `Realease` | 屬於發布/部署相關 | `ccdf2d00-7dc5-44c9-b5b3-c54346444eae` |

若現有標籤不夠描述，可新增自訂標籤——在 patch-page 的 `multi_select` 中直接用 `{"name": "新標籤名"}` （不帶 id），Notion 會自動建立新選項。

### Step 4：產出評估報告（不動 Notion）

以表格方式向使用者呈現評估結果：

```
## 📊 評估報告

### ✅ 建議移至「待處理」

| Idea | 複雜度 | 實用 | 想實作 | 契合度 | 理由摘要 |
|------|--------|------|--------|--------|---------|
| XXX  | 👩‍💻👩‍💻   | 💪💪💪 | 🔥🔥   | ❤️❤️❤️  | 核心延伸，利用現有爬蟲架構... |

### ☠️ 建議移至「廢棄」

| Idea | 原因 |
|------|------|
| XXX  | 技術複雜度過高，且與核心功能相關性低... |

### 📝 各 Idea 詳細分析
（每個 idea 的完整實作說明、技術限制、可拓展想法）
```

### Step 5：等待使用者確認

確認後，對每個 idea 依序執行：

**5-1. 更新量表 properties**
```
tool: mcp__claude_ai_Notion__notion-update-page
params:
  page_id: <idea_page_id>
  command: "update_properties"
  properties:
    複雜度: "<顯示值，如 👩‍💻👩‍💻>"
    實用程度: "<顯示值，如 💪💪💪>"
    想實作度: "<顯示值，如 🔥🔥>"
    產品契合度: "<顯示值，如 ❤️❤️❤️>"
    狀態: "<狀態名稱，如 🧐 待處理>"
    標籤: "<逗號分隔，如 前端,後端>"
  content_updates: []
```

**5-2. 在 Notion 頁面內容寫入分析**

先用 `mcp__claude_ai_Notion__notion-fetch` 讀取頁面現有內容，再用 `mcp__claude_ai_Notion__notion-update-page` 的 `update_content` 或 `replace_content` 加入以下區塊：

```
## 🤖 AI 評估（<日期>）

### 實作方法
<具體技術路徑，例：在 app/services/ 新增 xxx_service.py，新增 /api/xxx 路由>

### 技術限制
<已知障礙或前置依賴>

### 可拓展的想法
<這個功能完成後能衍伸的方向>

### 評估結論
<為何移至待處理/廢棄的理由>
```

## 重要注意事項

- **不使用「清空量表屬性」按鈕**——那是使用者自己管理用的
- 分析要根據 YGOscraper 的實際架構（FastAPI + React），不要寫泛用建議
- 若 idea 的補充資訊已有足夠描述，分析要與之對齊而非忽略
- 更新狀態時用 status option 的 **name**（不是 ID），因 Notion API patch-page 對 status 欄位的行為不同

## 附加資源

- **`../feature-idea-triage/SKILL.md`** — Property ID 和 Select 選項 ID 參考表
- **`references/notion-api-patterns.md`** — Notion API 操作範例
