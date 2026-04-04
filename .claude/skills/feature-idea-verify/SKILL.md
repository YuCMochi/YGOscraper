---
name: Feature Idea Verify
description: This skill should be used when checking if "已排程" feature ideas have been implemented in the codebase, or when the user says "檢查有沒有實作完"、"幫我看哪些功能做了"、"確認實作進度"、"更新 Notion 狀態". Triggered by feature-idea-triage or directly. Scans codebase and reports which features are done, then updates Notion after user confirmation.
version: 0.1.0
---

# Feature Idea Verify

掃描 codebase 確認「🗓️ 已排程」的 idea 是否已實作，向使用者報告結果，取得確認後更新 Notion 狀態至「✅ 已實作」並在 DEVELOPMENT_PLAN.md 打勾。

**所有 Notion 更新在取得使用者確認後才執行。**

## 執行流程

### Step 1：讀取「已排程」idea

從 triage 取得所有「🗓️ 已排程」的 idea，並讀取每個 idea 的 Notion 頁面內容，確認：

**若沒有任何「🗓️ 已排程」的 idea，向使用者報告「目前沒有已排程待驗證的 idea」並停止執行。**
- evaluate 寫的「實作方法」（應在頁面 block 中）
- plan 寫的「排程記錄」（對應哪個版本、哪些檔案）

### Step 2：讀取 DEVELOPMENT_PLAN.md

`docs/DEVELOPMENT_PLAN.md` 是「官方排程記錄」，找到每個 idea 對應的 checkbox 項目，確認哪些已打勾（`[x]`）、哪些未打勾（`[ ]`）。

### Step 3：掃描 codebase 驗證實作

根據 plan 中寫的實作路徑，逐一驗證：

**後端**（`app/` 目錄）
- 新增的 service 檔案是否存在（`app/services/xxx.py`）
- 新增的 router 是否存在，端點是否有對應 function
- config、schemas 是否更新

**前端**（`frontend/src/` 目錄）
- 新增的 component 是否存在
- 頁面是否有實際使用新功能的 code
- API 呼叫是否已對應

**驗證策略（依序使用）**
1. `grep_search` 搜尋關鍵 function 名稱、class 名稱、端點路徑
2. `list_dir` 確認檔案是否存在
3. `view_file` 確認檔案內容是否符合

### Step 4：產出驗證報告

向使用者呈現：

```
## 🔍 已排程功能實作驗證報告

### ✅ 確認已實作

| Idea | 驗證依據 |
|------|---------|
| config.py 依賴網址驗證 | `app/config.py` 有 `check_urls()` function，`server.py` 啟動時呼叫 |

### ⏳ 尚未實作 / 部分實作

| Idea | 缺少什麼 |
|------|---------|
| 全域設定 UI | 後端 API 存在，但 `frontend/src/` 中找不到 GlobalSettings component |

### ❓ 無法確認（需人工驗證）

| Idea | 原因 |
|------|------|
| XXX | 實作說明不夠具體，無法定位對應程式碼 |
```

### Step 5：等待使用者確認

使用者確認「✅ 確認已實作」清單後，對每個確認完成的 idea 執行：

**5-1. 更新 Notion 狀態**
```
tool: mcp__claude_ai_Notion__notion-update-page
params:
  page_id: <idea_page_id>
  command: "update_properties"
  properties:
    狀態: "✅ 已實作"
  content_updates: []
```

**5-2. 在 Notion 頁面新增完成記錄**

先用 `mcp__claude_ai_Notion__notion-fetch` 讀取頁面末尾，再 `update_content` append：

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

        ## ✅ 實作完成（<日期>）

        驗證依據：<驗證時找到的檔案/function>
```

**5-3. 在 DEVELOPMENT_PLAN.md 打勾**

將對應 checkbox `- [ ]` 改為 `- [x]`（使用 `Edit` 工具，提供足夠的上下文確保唯一匹配）。

## 常見實作位置速查

| 功能類型 | 預期位置 |
|---------|---------|
| 後端 API | `app/routers/*.py` |
| 業務邏輯 | `app/services/*.py` |
| 資料模型 | `app/schemas.py` |
| 外部 URL | `app/config.py` |
| 前端頁面 | `frontend/src/pages/*.jsx` |
| 前端元件 | `frontend/src/components/*.jsx` |
| 前端 API 呼叫 | `frontend/src/api.js` |
| 常數/設定 | `frontend/src/constants/*.js` |

## 注意事項

- 「已在 DEVELOPMENT_PLAN.md 打勾」不代表真的實作完——要實際掃 code
- 反之「code 存在」但 Notion 還是「已排程」的，也要一起更新
- 「部分實作」不更新到「✅ 已實作」，只報告缺少什麼
- 如果 evaluate 的實作說明太模糊，優先用 DEVELOPMENT_PLAN.md 的 checkbox 描述來定位

## 附加資源

- **`../feature-idea-triage/SKILL.md`** — Property ID 和 Status ID 參考表
- **`references/notion-api-patterns.md`** — Notion API 操作範例
