## ADDED Requirements

### Requirement: PR CI Workflow
系統 SHALL 有一個 GitHub Actions workflow (`ci.yml`)，在每個 PR 到 `main` 分支時自動觸發。

#### Scenario: PR 觸發 CI
- **WHEN** 開發者開一個 PR target 到 `main`
- **THEN** CI workflow SHALL 自動開始執行

#### Scenario: Push 到 PR branch 觸發 CI
- **WHEN** 開發者 push commits 到已存在的 PR branch
- **THEN** CI workflow SHALL 重新執行

---

### Requirement: Backend Lint Job
CI workflow SHALL 包含一個 backend lint job，使用 ruff 檢查 Python 程式碼品質。

#### Scenario: Lint 通過
- **WHEN** 所有 Python 檔案符合 ruff 規則
- **THEN** backend-lint job SHALL 通過（exit code 0）

#### Scenario: Lint 失敗
- **WHEN** 有 Python 檔案違反 ruff 規則
- **THEN** backend-lint job SHALL 失敗並顯示違規細節

---

### Requirement: Backend Test Job
CI workflow SHALL 包含一個 backend test job，執行 pytest（排除 integration marker）。

#### Scenario: 所有 unit tests 通過
- **WHEN** `pytest -m "not integration"` 所有測試通過
- **THEN** backend-test job SHALL 通過

#### Scenario: 有 test 失敗
- **WHEN** 任一 unit test 失敗
- **THEN** backend-test job SHALL 失敗，PR 不能 merge

---

### Requirement: Frontend Lint Job
CI workflow SHALL 包含一個 frontend lint job，執行 `npm run lint`。

#### Scenario: ESLint 通過
- **WHEN** 所有前端檔案通過 ESLint 檢查
- **THEN** frontend-lint job SHALL 通過

---

### Requirement: Frontend Build Job
CI workflow SHALL 包含一個 frontend build job，執行 `npm run build` 確保 production build 正常。

#### Scenario: Build 成功
- **WHEN** `npm run build` 成功完成
- **THEN** frontend-build job SHALL 通過

#### Scenario: Build 失敗
- **WHEN** TypeScript 錯誤或 import 問題導致 build 失敗
- **THEN** frontend-build job SHALL 失敗，PR 不能 merge
