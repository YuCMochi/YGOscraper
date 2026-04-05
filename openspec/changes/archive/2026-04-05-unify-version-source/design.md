## Context

目前版本號散落於四處：
- `server.py`：`version="0.3.0"`（FastAPI app 元數據）
- `frontend/src/components/Layout.jsx`：hard-coded `v0.4.1`
- `frontend/package.json`：`"version": "2.0.0"`（毫無語意）
- `README.md`：標題 `v0.3.0`

真實版本為 v0.4.1。`server.py` 的 FastAPI `version` 欄位會自動出現在 `/openapi.json` 和 Swagger UI，也可透過 `app.version` 在任何 router 存取，是天然的單一真相來源。

## Goals / Non-Goals

**Goals:**
- 確立 `server.py` 的 `version` 欄位為唯一版本號真相來源
- 前端版本號顯示改為動態讀取，消除 hard-code
- 所有硬編碼位置統一更新至 v0.4.1
- 補打 git annotated tag `v0.4.1`，建立後續打 tag 慣例

**Non-Goals:**
- 自動化 bump 腳本（目前規模不需要）
- CI/CD release pipeline
- Semantic versioning 嚴格驗證

## Decisions

**決策 1：版本號真相來源選 `server.py`**

FastAPI 的 `app.version` 已存在且有明確語意。任何 router 都可透過 `request.app.version` 讀取，不需新增額外設定檔。

替代方案：`pyproject.toml` 的 `[project] version` — 需要額外的讀檔邏輯，且 `pyproject.toml` 目前只用於 pytest/ruff 設定，語意不符。

**決策 2：新增 `GET /api/version` endpoint**

在 `health.py` 或新建一個輕量 endpoint 回傳 `{"version": "x.x.x"}`。前端 `Layout.jsx` 在 mount 時呼叫一次，顯示結果；若 API 失敗則 fallback 顯示 `"—"`。

替代方案：讓前端直接解析 `/openapi.json` 取得版本——路徑太長，且 openapi.json 是大型 JSON，浪費流量。

**決策 3：`package.json` version 固定 `0.0.0`**

此欄位只在 npm publish 時有意義，此專案不發布套件。固定 `0.0.0` 明確表示「此欄位不維護」，比亂填一個數字更誠實。

**決策 4：git tag 使用 annotated tag**

```bash
git tag -a v0.4.1 -m "Release v0.4.1"
```

Annotated tag 有作者、時間、訊息，`git describe` 也能正確使用。Lightweight tag 只是指標，缺少元數據。

## Risks / Trade-offs

- **前端版本號多一次 API 請求** → 影響極微（只在 mount 時發一次，且版本號不影響功能）。若後端未啟動，顯示 `"—"` 而非錯誤。
- **`server.py` 仍需手動更新** → 接受。在真正需要自動化之前（如 CI/CD release），手動維護一個地方的成本可接受。

## Migration Plan

1. 更新 `server.py` version → `"0.4.1"`
2. 在 `app/routers/health.py` 新增 `GET /api/version` endpoint
3. 更新 `Layout.jsx`：移除 hard-coded 字串，改為 `useEffect` 呼叫 `/api/version`
4. 更新 `frontend/package.json` version → `"0.0.0"`
5. 更新 `README.md` 標題與版本表格
6. 執行 `git tag -a v0.4.1 -m "Release v0.4.1"`

Rollback：若前端 API 呼叫有問題，可暫時 hard-code 回來，無資料遷移風險。