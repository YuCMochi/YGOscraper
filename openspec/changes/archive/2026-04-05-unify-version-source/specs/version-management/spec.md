## ADDED Requirements

### Requirement: Single source of truth for version number
系統 SHALL 以 `server.py` 的 FastAPI `version` 參數作為唯一版本號真相來源。任何其他位置的版本號顯示 SHALL 動態取得，不得硬編碼。

#### Scenario: Backend exposes version via API
- **WHEN** 客戶端發送 `GET /api/version`
- **THEN** 系統回傳 `{"version": "<current_version>"}` 且 HTTP 200

#### Scenario: Frontend displays version from API
- **WHEN** 使用者載入前端應用程式
- **THEN** 左側欄底部顯示的版本號與 `GET /api/version` 回傳值一致

#### Scenario: Frontend handles API failure gracefully
- **WHEN** `GET /api/version` 請求失敗（後端未啟動或網路錯誤）
- **THEN** 前端版本號顯示區塊顯示 `"—"` 而非錯誤訊息或空白

### Requirement: Git tag marks each milestone
專案 SHALL 在每個里程碑版本完成時打上對應的 annotated git tag，格式為 `v<major>.<minor>.<patch>`。

#### Scenario: Annotated tag exists for current version
- **WHEN** 執行 `git tag -l "v<current_version>"`
- **THEN** 輸出包含對應版本的 tag

#### Scenario: Tag contains release message
- **WHEN** 執行 `git show v<current_version>`
- **THEN** 輸出包含 tag 訊息（非 lightweight tag）