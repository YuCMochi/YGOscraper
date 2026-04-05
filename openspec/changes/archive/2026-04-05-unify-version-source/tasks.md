## 1. 後端：確立版本號真相來源

- [x] 1.1 更新 `server.py` 的 `version` 參數：`"0.3.0"` → `"0.4.1"`
- [x] 1.2 在 `app/routers/health.py` 新增 `GET /api/version` endpoint，從 `request.app.version` 讀取並回傳 `{"version": "x.x.x"}`

## 2. 前端：動態讀取版本號

- [x] 2.1 更新 `frontend/package.json` 的 `version`：`"2.0.0"` → `"0.0.0"`
- [x] 2.2 修改 `frontend/src/components/Layout.jsx`：移除 hard-coded `v0.4.1`，改以 `useEffect` + `useState` 呼叫 `GET /api/version`，失敗時顯示 `"—"`

## 3. 文件更新

- [x] 3.1 更新 `README.md` 標題：`# ⚡ YGO Scraper v0.3.0` → `v0.4.1`
- [x] 3.2 在 `README.md` 版本表格中補上 `v0.3.1`、`v0.4.0`、`v0.4.1` 的紀錄

## 4. Git Tag

- [x] 4.1 執行 `git tag -a v0.4.1 -m "Release v0.4.1"` 補打目前 HEAD 的 annotated tag
- [x] 4.2 確認 tag 正確：`git show v0.4.1` 應顯示 tag 訊息與指向的 commit