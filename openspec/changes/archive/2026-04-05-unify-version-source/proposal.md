## Why

版本號目前硬編碼散落於 `server.py`、`frontend/package.json`、`Layout.jsx`、`README.md` 四個地方，每次里程碑推進都需手動更新多處，實際上各處已不一致（現在是 v0.4.1，但 `server.py` 仍顯示 0.3.0，README 顯示 v0.3.0）。此外專案從未使用 git tag 標記里程碑，版本歷史只能靠 commit 訊息猜測。

## What Changes

- 確立 `server.py` 的 `version` 欄位為唯一版本號真相來源，更新至 `0.4.1`
- `Layout.jsx` 改為從後端 `/` 或 `/health` API 動態讀取版本號，移除 hard-coded 字串
- `frontend/package.json` 的 version 固定為 `0.0.0`，不再維護（此欄位對非 npm 發布專案無意義）
- 更新 `README.md` 標題與版本歷史至 v0.4.1
- 補打 git tag `v0.4.1` 指向目前 HEAD，並確立後續里程碑打 tag 的慣例

## Capabilities

### New Capabilities

- `version-management`: 版本號單一來源管理——後端為真相來源，前端動態讀取，搭配 git tag 標記里程碑

### Modified Capabilities

（無現有 spec 層級的行為變更）

## Impact

- `server.py`: version 欄位從 `0.3.0` 更新至 `0.4.1`
- `frontend/src/components/Layout.jsx`: 移除 hard-coded `v0.4.1`，改為 API 呼叫
- `frontend/package.json`: version 從 `2.0.0` 改為 `0.0.0`
- `README.md`: 標題與版本表格更新
- git: 補打 `v0.4.1` annotated tag