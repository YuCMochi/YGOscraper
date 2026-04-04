---
name: Feature Idea Plan
description: This skill should be used when the user wants to schedule a "待處理" feature idea into the development plan, or says "把這個排進去"、"幫我規劃實作"、"加進開發計劃"、"排程這個功能". Triggered by feature-idea-triage or directly. Creates a GitHub Issue, assigns it to the appropriate milestone, and updates Notion status to "已排程".
version: 0.2.0
---

# Feature Idea Plan

將「🧐 待處理」的 idea 轉化為實際開發計畫：在 GitHub 建立 Issue 並指定 Milestone，在 Notion 更新狀態為「🗓️ 已排程」。

**所有動作在取得使用者確認後才執行。**

## 執行流程

### Step 1：讀取「待處理」idea

從 triage 資料或直接查詢取得所有「🧐 待處理」的 idea，並用 `mcp__claude_ai_Notion__notion-fetch` 讀取每個 idea 的頁面內容（properties 與內容一次取得，應已有評估分析）。

**若沒有任何「🧐 待處理」的 idea，向使用者報告「目前沒有待排程的 idea」並停止執行。**

### Step 2：閱讀版本路線圖

用 `gh api repos/YuCMochi/YGOscraper/milestones` 列出現有 Milestones，理解：
- 目前各版本（v0.5.0、v0.6.0 等）已規劃的內容
- 哪個版本最適合放入這個 idea
- 版本的技術主題（例如 v0.5.0 主題是「爬蟲升級」，相關功能就放這裡）

### Step 3：決定排程版本

**版本選擇邏輯**：
- 依賴現有版本功能才能做的 → 排在依賴版本之後
- 屬於某個技術主題的 → 放進對應主題版本
- 獨立功能 → 依複雜度，輕量放近期版本，重量放遠期或新建版本
- 非常遠期/實驗性 → 考慮放 v1.0.0 milestone

若現有 milestone 都不合適，可用 `gh api repos/YuCMochi/YGOscraper/milestones --method POST -f title="vX.X.X — <主題>"` 建立新 milestone。

### Step 4：產出排程計畫草稿

向使用者呈現：

```
## 📅 排程建議

### <Idea 名稱>  →  <目標版本>

**GitHub Issue 內容**：
- Title：<Issue 標題>
- Milestone：<版本號>
- Body 摘要：<實作項目說明>

**理由**：<為什麼放在這個版本>

---
（多個 idea 依此格式列出）
```

### Step 5：等待使用者確認

確認後執行：

**5-1. 建立 GitHub Issue**

```bash
gh issue create \
  --title "<Idea 名稱>" \
  --body "<實作項目說明，含依賴關係、技術路徑>" \
  --label "enhancement" \
  --milestone "<版本號> — <版本主題>"
```

將回傳的 Issue URL 記下（後續寫入 Notion）。

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

        已排入 <版本號>，GitHub Issue：<Issue URL>
        預計實作內容：<摘要>
```

## 版本路線圖現況摘要

（供快速決策用，詳細資訊用 `gh api repos/YuCMochi/YGOscraper/milestones` 查詢）

| 版本 | 主題 | Milestone # |
|------|------|-------------|
| v0.5.0 | 爬蟲升級（items/v2 API） | #1 |
| v0.6.0 | Neuron 牌組導入 | #2 |
| v0.7.0 | 前端重構 + UX 打磨 | #3 |
| v1.0.0 | 正式版 | #4 |

## 注意事項

- GitHub Issue 的 body 要夠具體，讓未來的 AI（包含自己）一看就知道要實作什麼
- 子任務要對應到實際的檔案/模組層級（例如「新增 `app/services/neuron_service.py`」）
- 若 idea 已有 evaluate 寫的分析，直接沿用技術路徑，不要重複設計
- 若有依賴關係，在 Issue body 用 `（依賴 #N）` 的格式標明

## 附加資源

- **`../feature-idea-triage/SKILL.md`** — Property ID 和 Status ID 參考表
- **`references/notion-api-patterns.md`** — Notion API 操作範例
