# Notion API 操作範例

這份文件是 Feature Idea skills 的共用 Notion API 參考。
使用的 MCP 是 **claude.ai Notion integration**，tool 前綴為 `mcp__claude_ai_Notion__`。

---

## 讀取 Feature idea 資料庫（取得所有 idea）

**Step 1：先 fetch 資料庫，取得 collection URL**

```
tool: mcp__claude_ai_Notion__notion-fetch
params:
  id: "551e2978-dbb8-82fb-91fd-01d2e67dd45b"   # Feature idea 資料庫 ID

# 回傳中會有 <data-source url="collection://..."> 標籤，記錄該 URL
```

**Step 2：用 collection URL 搜尋所有 idea**

```
tool: mcp__claude_ai_Notion__notion-search
params:
  query: "idea"
  query_type: "internal"
  data_source_url: "collection://<從 fetch 取得的 collection ID>"
  page_size: 25
  filters: {}

# 可多次呼叫，搭配不同 query 確保涵蓋所有條目
# 根據狀態欄位過濾分類（回傳的 properties 會包含狀態值）
```

---

## 讀取單一 idea 頁面（properties + 內容一次取得）

```
tool: mcp__claude_ai_Notion__notion-fetch
params:
  id: "<idea_page_id>"

# 同一個 call 同時回傳：
# - properties（量表、狀態等）
# - 頁面內文 blocks（評估分析、排程記錄等）
# 不需要另外呼叫 get-block-children
```

---

## 更新 properties（量表 + 狀態）

```
tool: mcp__claude_ai_Notion__notion-update-page
params:
  page_id: "<idea_page_id>"
  command: "update_properties"
  properties:
    狀態: "🧐 待處理"          # status → 用顯示名稱字串
    複雜度: "👩‍💻👩‍💻"             # select → 用顯示值字串
    實用程度: "💪💪💪"          # select → 用顯示值字串
    想實作度: "🔥🔥🔥"          # select → 用顯示值字串
    產品契合度: "❤️❤️❤️"        # select → 用顯示值字串
  content_updates: []
```

> ⚠️ claude.ai Notion tool 的 properties 使用 **SQLite 值（字串）**，不是 raw Notion API 的 `{ status: { name: "..." } }` 格式

---

## 在頁面新增內容

使用 `update_content` 搜尋特定位置後插入，或用 `replace_content` 整頁覆寫。

**append 新內容（在頁面底部加入）**

先用 `notion-fetch` 取得頁面現有內容，找到最後一段，然後 append：

```
tool: mcp__claude_ai_Notion__notion-update-page
params:
  page_id: "<idea_page_id>"
  command: "update_content"
  properties: {}
  content_updates:
    - old_str: "<頁面最後一行的現有內容>"
      new_str: |
        <頁面最後一行的現有內容>

        ## 🤖 AI 評估（2026-04-03）

        ### 實作方法
        在 app/services/ 新增 xxx_service.py...

        ### 技術限制
        ...

        ---
```

> ⚠️ `update_content` 是 search-and-replace，`old_str` 必須完全符合頁面現有內容
> ⚠️ 若頁面是空的，改用 `replace_content` 直接寫入全部內容

**replace_content（整頁覆寫，適合空頁面）**

```
tool: mcp__claude_ai_Notion__notion-update-page
params:
  page_id: "<idea_page_id>"
  command: "replace_content"
  properties: {}
  content_updates: []
  new_str: |
    ## 🤖 AI 評估（2026-04-03）

    ### 實作方法
    ...
```

---

## 狀態更新速查表

| 目標狀態 | properties 值 |
|---------|--------------|
| 未開始 | `"📥 未開始"` |
| 待處理 | `"🧐 待處理"` |
| 已排程 | `"🗓️ 已排程"` |
| 已實作 | `"✅ 已實作"` |
| 廢棄 | `"☠️ 廢棄"` |

---

## 量表欄位值速查表

### 複雜度（property: `複雜度`）

| 顯示值 | properties 字串 |
|--------|----------------|
| 👩‍💻 | `"👩‍💻"` |
| 👩‍💻👩‍💻 | `"👩‍💻👩‍💻"` |
| 👩‍💻👩‍💻👩‍💻 | `"👩‍💻👩‍💻👩‍💻"` |

### 實用程度（property: `實用程度`）

| 顯示值 | properties 字串 |
|--------|----------------|
| 💪 | `"💪"` |
| 💪💪 | `"💪💪"` |
| 💪💪💪 | `"💪💪💪"` |

### 想實作度（property: `想實作度`）

| 顯示值 | properties 字串 |
|--------|----------------|
| 🔥 | `"🔥"` |
| 🔥🔥 | `"🔥🔥"` |
| 🔥🔥🔥 | `"🔥🔥🔥"` |

### 產品契合度（property: `產品契合度`）

| 顯示值 | properties 字串 |
|--------|----------------|
| ❤️ | `"❤️"` |
| ❤️❤️ | `"❤️❤️"` |
| ❤️❤️❤️ | `"❤️❤️❤️"` |

---

## 標籤（multi_select）操作

標籤欄位用逗號分隔的字串（全量覆蓋，要保留現有標籤就必須全部列出）：

```
tool: mcp__claude_ai_Notion__notion-update-page
params:
  page_id: "<idea_page_id>"
  command: "update_properties"
  properties:
    標籤: "前端,後端"    # 逗號分隔；若需要新標籤直接加名稱，Notion 自動建立
  content_updates: []
```

> ⚠️ 若不確定 multi_select 格式，先用 `notion-fetch` 讀取現有標籤，確認回傳格式後再更新

---

## Property 欄位名稱參考

| 欄位顯示名 | update_properties 用的 key |
|-----------|--------------------------|
| Idea 名稱 | `Idea名稱`（title） |
| 狀態 | `狀態` |
| 複雜度 | `複雜度` |
| 實用程度 | `實用程度` |
| 想實作度 | `想實作度` |
| 產品契合度 | `產品契合度` |
| 補充資訊 | `補充資訊` |
| 標籤 | `標籤` |

> 若欄位 key 不確定，先 `notion-fetch` 頁面後看 properties 的實際 key 名稱
