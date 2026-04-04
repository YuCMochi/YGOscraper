---
name: Feature Idea Triage
description: This skill should be used when the user mentions "開發新 feature"、"有新想法"、"看看 Notion 上有什麼"、"幫我整理 feature"、"我想加一個功能"、"你去 Notion 看看"，或者在討論新功能方向時。這是 Feature Idea 管理系統的主入口，負責讀取整個 Notion Feature idea 資料庫現況並決定後續行動。
version: 0.1.0
---

# Feature Idea Triage

這是 YGOscraper Feature idea 管理系統的**主入口 skill**。負責總攬 Notion 資料庫現況，並決定要呼叫哪個子 skill 執行後續工作。

## 核心資訊

**Notion Feature idea 資料庫**
- Database ID: `551e2978-dbb8-82fb-91fd-01d2e67dd45b`
- 父頁面：YGO scraper (`1a0e2978-dbb8-8040-bf63-f5f21400e044`)

**狀態選項 ID（更新 Notion 時必用）**

| 狀態 | 名稱 | ID |
|------|------|----|
| 📥 未開始 | `📥 未開始` | `570e2916-9b30-4340-af81-27d33a8185f4` |
| 🧐 待處理 | `🧐 待處理` | `64ce64de-aac2-4e97-856e-4d9d04b66172` |
| 🗓️ 已排程 | `🗓️ 已排程` | `a2c9b3ef-6486-4dae-ba07-74087d8d2119` |
| ✅ 已實作 | `✅ 已實作` | `U35BPg` |
| ☠️ 廢棄 | `☠️ 廢棄` | `b3b58f5f-b4ff-4a1c-b170-0792a3f5994b` |

**狀態流程**
```
📥 未開始 → (evaluate) → 🧐 待處理 或 ☠️ 廢棄
🧐 待處理 → (plan)     → 🗓️ 已排程
🗓️ 已排程 → (verify)   → ✅ 已實作
```

## Triage 執行流程

### Step 1：讀取全部 idea

先用 `mcp__claude_ai_Notion__notion-fetch` 帶入資料庫 ID，取得回傳中的 `collection://` URL。
再用 `mcp__claude_ai_Notion__notion-search` 搭配 `data_source_url` 列出所有 idea 條目。

詳細操作範例見 `references/notion-api-patterns.md`。

### Step 2：分類整理

將所有 idea 按狀態分組統計。對每個 idea 記錄：
- Idea 名稱
- 狀態
- 是否有補齊量表（複雜度/實用程度/想實作度/產品契合度）
- 補充資訊摘要

### Step 3：報告現況並決定行動

向使用者報告現況摘要（表格形式），然後依據以下規則決定下一步：

| 有什麼 | 建議行動 |
|--------|---------|
| 有「未開始」的 idea | → 呼叫 `feature-idea-evaluate` skill |
| 有「待處理」的 idea | → 詢問使用者是否要排程，再呼叫 `feature-idea-plan` skill |
| 有「已排程」的 idea | → 呼叫 `feature-idea-verify` skill 檢查是否已實作 |
| 以上皆無 | → 告知使用者目前 backlog 已清空 |

多種狀態同時存在時，**依上表順序**依次提出，請使用者決定優先處理哪個。

### Step 4：等待使用者確認

Triage 本身**不做任何 Notion 寫入操作**，只負責讀取和決策。所有實際修改由子 skill 執行，並在執行前取得使用者確認。

## 欄位 Property ID 參考（更新頁面 properties 時使用）

| 欄位名稱 | Property ID | 類型 |
|--------|------------|------|
| Idea名稱 | `title` | title |
| 狀態 | `wf_S` | status |
| 複雜度 | `NDpu` | select |
| 實用程度 | `U{gD` | select |
| 想實作度 | `UDF\|` | select |
| 產品契合度 | `\|[:\` | select |
| 補充資訊 | `:}_M` | rich_text |
| 標籤 | `zdph` | multi_select |

## Select 欄位選項 ID

**複雜度**
- `複雜度: 👩‍💻` → `c3c1fd9b-1d25-4a93-abfa-a11640080f24`
- `複雜度: 👩‍💻👩‍💻` → `f68b134f-e4e9-478d-8042-ed0d29ec5aee`
- `複雜度: 👩‍💻👩‍💻👩‍💻` → `d9f00fa0-c30c-492a-81f1-a0b7408c14b8`

**實用程度**
- `實用程度: 💪💪💪` → `e4334636-5c07-4e04-bc4c-c7f1dc2299d9`
- `實用程度: 💪💪` → `9a9750b2-3209-4a41-8e50-582bb39a097d`
- `實用程度: 💪` → `4f1b6718-c45a-4642-8070-eb822c924cd4`

**想實作度**
- `想實作度: 🔥🔥🔥` → `62b7cab8-8e62-4af0-882e-4abcc7a53b2e`
- `想實作度: 🔥🔥` → `41004201-a899-458c-9940-803e939472fb`
- `想實作度: 🔥` → `4aa24e42-d806-44bb-8797-98c393259d80`

**產品契合度**
- `契合度: ❤️❤️❤️` → `f22feb86-f346-40de-be0f-82a09b593c47`
- `契合度: ❤️❤️` → `d22fbcc8-43a8-454b-bc6f-f8e588769c7c`
- `契合度: ❤️` → `8d4659df-b336-40fa-9992-b6f9eccd3433`

## 附加資源

更詳細的評估標準、排程規則請參考各子 skill：
- **`../feature-idea-evaluate/SKILL.md`** — 評估「未開始」idea 的完整流程
- **`../feature-idea-plan/SKILL.md`** — 將「待處理」排入開發計畫的流程
- **`../feature-idea-verify/SKILL.md`** — 驗證「已排程」是否已實作的流程
- **`references/notion-api-patterns.md`** — Notion API 操作範例
