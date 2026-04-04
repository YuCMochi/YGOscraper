---
name: Feature Idea Plan
description: This skill should be used when the user wants to schedule a "待處理" feature idea into the development plan, or says "把這個排進去"、"幫我規劃實作"、"加進開發計劃"、"排程這個功能". Triggered by feature-idea-triage or directly. Writes implementation details to DEVELOPMENT_PLAN.md and updates Notion status to "已排程".
version: 0.1.0
---

# Feature Idea Plan

將「🧐 待處理」的 idea 轉化為實際開發計畫，寫入 `docs/DEVELOPMENT_PLAN.md` 並在 Notion 更新狀態為「🗓️ 已排程」。

**所有動作在取得使用者確認後才執行。**

## 執行流程

### Step 1：讀取「待處理」idea

從 triage 資料或直接查詢取得所有「🧐 待處理」的 idea，並用 `mcp__claude_ai_Notion__notion-fetch` 讀取每個 idea 的頁面內容（properties 與內容一次取得，應已有評估分析）。

**若沒有任何「🧐 待處理」的 idea，向使用者報告「目前沒有待排程的 idea」並停止執行。**

### Step 2：閱讀現有開發計畫

讀取 `docs/DEVELOPMENT_PLAN.md`，理解：
- 目前各版本（v0.3.0、v0.4.0 等）已規劃的內容
- 哪個版本最適合放入這個 idea
- 版本的技術主題（例如 v0.4.0 主題是「爬蟲升級」，相關功能就放這裡）

### Step 3：決定排程版本

**版本選擇邏輯**：
- 依賴現有版本功能才能做的 → 排在依賴版本之後
- 屬於某個技術主題的 → 放進對應主題版本
- 獨立功能 → 依複雜度，輕量放近期版本，重量放遠期或新建版本
- 非常遠期/實驗性 → 考慮放「更遠的未來」區段

若現有版本都不合適，可提議建立新版本（如 v0.7.0）。

### Step 4：產出排程計畫草稿

向使用者呈現：

```
## 📅 排程建議

### <Idea 名稱>  →  <目標版本>

**實作項目**（DEVELOPMENT_PLAN.md 新增的 checkbox items）：
- [ ] **<功能模組>**：<具體說明>
  - [ ] <子任務1>
  - [ ] <子任務2>

**插入位置**：<版本號> 的「<章節名稱>」之後

**理由**：<為什麼放在這個版本>

---
（多個 idea 依此格式列出）
```

### Step 5：等待使用者確認

確認後執行：

**5-1. 更新 DEVELOPMENT_PLAN.md**

在對應版本的 checklist 中新增實作項目（用 `Edit` 工具精確插入，提供足夠的上下文確保唯一匹配，不要改動現有內容）。

格式要與現有文件一致（使用相同的 markdown 風格）。

**5-2. 更新 Notion 狀態**

```
tool: mcp__claude_ai_Notion__notion-update-page
params:
  page_id: <idea_page_id>
  command: "update_properties"
  properties:
    狀態: "🗓️ 已排程"
  content_updates: []
```

**5-3. 在 Notion 頁面新增排程記錄**

先用 `mcp__claude_ai_Notion__notion-fetch` 讀取頁面末尾內容，再用 `update_content` append：

```
tool: mcp__claude_ai_Notion__notion-update-page
params:
  page_id: <idea_page_id>
  command: "update_content"
  properties: {}
  content_updates:
    - old_str: "<頁面最後一段現有內容>"
      new_str: |
        <頁面最後一段現有內容>

        ## 🗓️ 排程記錄（<日期>）

        已排入 <版本號>，對應 DEVELOPMENT_PLAN.md <版本號> 段落
        預計實作內容：<摘要>
```

## 版本路線圖現況摘要

（供快速決策用，詳細內容以 DEVELOPMENT_PLAN.md 為準）

| 版本 | 主題 | 狀態 |
|------|------|------|
| v0.2.0–v0.2.1 | 後端重構 + Bug 修復 | ✅ 完成 |
| v0.3.0 | 前端強化 + 全域設定 UI | ⬜ 計畫中 |
| v0.4.0 | 爬蟲升級（items/v2 API） | 💡 構想中 |
| v0.5.0 | Neuron 牌組導入 | 💡 構想中 |
| v0.6.0 | UX + UI 改善 | 💡 構想中 |
| v1.0.0 | 正式版 | 🎯 目標 |

## 注意事項

- 寫進 `DEVELOPMENT_PLAN.md` 的項目要夠具體，讓未來的 AI（包含自己）一看就知道要實作什麼
- 子任務要對應到實際的檔案/模組層級（例如「新增 `app/services/neuron_service.py`」）
- 若 idea 已有 evaluate 寫的分析，直接沿用技術路徑，不要重複設計
- 版本標題格式維持：`### vX.X.X — <主題> <狀態emoji>`

## 附加資源

- **`../feature-idea-triage/SKILL.md`** — Property ID 和 Status ID 參考表
- **`references/notion-api-patterns.md`** — Notion API 操作範例
