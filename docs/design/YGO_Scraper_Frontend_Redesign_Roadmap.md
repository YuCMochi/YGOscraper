# YGO Scraper 前端重構完整指南
## 業界標準 UI/UX 工作流 + 做中學

**版本**: v1.0  
**最後更新**: 2026-04-15  
**預計工期**: 4-6 週（深度學習版）

---

## 📋 目錄

1. [專案概述](#專案概述)
2. [第 1 階段：策略與研究](#第-1-階段策略與研究)
3. [第 2 階段：資訊架構與流程設計](#第-2-階段資訊架構與流程設計)
4. [第 3 階段：線框圖與可用性測試](#第-3-階段線框圖與可用性測試)
5. [第 4 階段：設計系統](#第-4-階段設計系統)
6. [第 5 階段：高保真設計](#第-5-階段高保真設計)
7. [第 6 階段：前端架構與開發](#第-6-階段前端架構與開發)
8. [第 7 階段：測試與最佳化](#第-7-階段測試與最佳化)
9. [第 8 階段：文檔與開源準備](#第-8-階段文檔與開源準備)
10. [學習成果清單](#學習成果清單)

---

## 專案概述

### 🎯 目標
- **使用者群體**: 遊戲王卡牌愛好者 + 開源開發者 + 小型電商
- **核心功能**: 自動比價、購物車管理、爬蟲結果可視化
- **開源方向**: 社群貢獻友善、清晰的代碼結構、完整文檔

### 📊 現狀問題
根據你的回答，現有 UI 的問題：
- **美觀度**: 不美觀（缺乏視覺層次和設計語言）
- **操作直覺性**: 操作不直覺（按鈕位置、流程邏輯不清晰）
- **功能組織**: 功能組織混亂（模組邊界不清）
- **性能**: 載入速度慢（可能的 React 最佳化機會）

### 🎓 學習目標
完成本計劃後，你將理解和掌握：
- ✅ 完整的 UX 設計流程（從研究到測試）
- ✅ 設計系統的建立與維護
- ✅ 前端架構最佳實踐
- ✅ 可訪問性 (A11y) 設計
- ✅ 開源專案的設計和代碼規範
- ✅ React 高級模式（狀態管理、效能最佳化）
- ✅ UI 元件庫的設計和實現

---

## 第 1 階段：策略與研究
**預計時間**: 3-4 天  
**交付物**: 使用者研究文檔 + 競品分析

### 1.1 定義使用者人物誌 (User Personas)

開源社群的多樣性高，至少定義 3-4 個代表性使用者：

#### 人物 1：「小智 - 認真集卡者」
```
年齡: 20-35 歲
背景: 遊戲王卡牌愛好者，購買力強
技能等級: 中等 (會用網購，不懂開發)
動機: 找最便宜的卡片，建立完整卡組

主要痛點:
  1. 手動比價太麻煩，容易漏掉便宜選項
  2. 不知道如何組合購買才最便宜
  3. 需要導出清單給朋友或店家
  4. 卡片密碼轉換（密碼 ↔ 卡號）複雜

期望:
  - 簡單直覺的搜尋
  - 一鍵加入購物車
  - 自動計算最優方案
  - 可導出採購清單
  - 支援批量操作

使用場景:
  • 晚上 1-2 小時，批量搜尋 10-20 張卡
  • 與朋友湊單時需要共享
  • 手機和桌機都要用
```

#### 人物 2：「開發者大衛」
```
年齡: 25-40 歲
背景: 全棧開發者，開源愛好者
技能等級: 高等 (熟悉 React, Python, DevOps)
動機: 為社群做貢獻，學習新技術

主要痛點:
  1. 代碼組織不清晰，難以貢獻
  2. 缺少設計文檔，UI 改動無依據
  3. 想添加新爬蟲源，後端 API 不夠清晰
  4. 沒有自動化測試和 CI/CD

期望:
  - 模組化的代碼結構
  - 完整的 API 文檔和設計系統
  - 清晰的 CONTRIBUTING.md
  - 自動化測試框架
  - 歡迎 PR 的開發流程

使用場景:
  • 週末研究代碼，修復 bug
  • 計畫添加 Yahoo 拍賣爬蟲
  • 建議 UI 改進
```

#### 人物 3：「店主小黃」
```
年齡: 35-50 歲
背景: 開卡牌店，需要降低進貨成本
技能等級: 低 (只會基本電腦操作)
動機: 自動化進貨流程，節省時間

主要痛點:
  1. 進貨單據龐大（百張以上），手動很困難
  2. 需要定時監控價格變動
  3. 必須 24/7 穩定運行
  4. 需要導出 CSV 給會計

期望:
  - 穩定可靠的系統
  - 簡單的批量上傳介面
  - 自動化定時任務
  - 可導出數據的功能
  - 長期的技術支援

使用場景:
  • 每週一早上上傳 100 張卡的進貨清單
  • 檢視過去一週的價格趨勢
  • 導出採購報告給員工
```

### 1.2 使用者旅程地圖 (User Journey Map)

以小智為例，詳細映射他的完整使用旅程：

```
階段 1: 發現與開始
  觸發點: 想買新卡組的卡片
  接觸點: Google 搜尋 → 找到 YGO Scraper GitHub
  心理: 「這個工具看起來不錯，但我不確定怎麼用」
  需求: 清晰的首頁說明和快速教學

階段 2: 新建專案
  動作: 點擊「新建專案」，輸入專案名稱
  接觸點: 新建對話框 / 表單
  心理: 「為什麼要建專案？這能幫我什麼？」
  需求: 簡單的表單，有提示文字說明作用

階段 3: 搜尋和加購物車
  動作: 搜尋「青眼白龍」，看搜尋結果，點擊「加入購物車」
  接觸點: 搜尋框 → 卡片列表 → 按鈕
  心理: 「結果出現了，但我如何確認是正確的卡？」
  需求: 
    - 清晰的卡片展示（圖片、密碼、名稱）
    - 快速添加按鈕（大且醒目）
    - 反饋提示（「已加入購物車」提示）

階段 4: 重複搜尋
  動作: 搜尋「增殖的G」、「無限泡影」等 10 張卡
  接觸點: 重複搜尋框和點擊
  心理: 「一張張搜太慢了，有沒有快速方式？」
  需求:
    - 搜尋記錄快速建議
    - 批量輸入選項（貼上多個卡名）
    - 最近搜尋清單

階段 5: 檢視購物車
  動作: 點開購物車，查看已加入的卡片
  接觸點: 購物車側邊欄 / 彈窗
  心理: 「確認我加了哪些卡，我可以改數量嗎？」
  需求:
    - 清晰的列表 UI（卡片名稱、數量、密碼）
    - 可編輯數量的輸入框
    - 移除按鈕
    - 購物車摘要（共幾張卡）

階段 6: 調整全域設定
  動作: 設定運費、最小消費、排除詞
  接觸點: 側邊欄設定面板
  心理: 「這些設定會影響爬蟲結果，我要設定正確」
  需求:
    - 清晰的選項說明
    - 預設值建議
    - 儲存反饋

階段 7: 執行爬蟲
  動作: 點擊「執行爬蟲」按鈕，等待結果
  接觸點: 大按鈕 + 進度指示器
  心理: 「爬蟲在執行，我該等多久？正常嗎？」
  需求:
    - 清晰的爬蟲進度條
    - 預估時間
    - 能取消的選項
    - 進度日誌（哪些卡片已搜尋）

階段 8: 檢視結果
  動作: 查看最優採購方案，瀏覽各家賣家報價
  接觸點: 結果頁面（表格 / 卡片）
  心理: 「這個方案為什麼最便宜？我怎樣確保不出錯？」
  需求:
    - 清晰的比價表（卡片、卡號、賣家、價格、運費）
    - 推薦方案的說明
    - 查看詳細報價的功能

階段 9: 導出與購買
  動作: 導出清單 → 前往露天拍賣購買
  接觸點: 「導出 CSV」按鈕 / 超連結
  心理: 「我要把資料給朋友，怎樣最方便？」
  需求:
    - 多種導出格式（CSV、PDF、分享連結）
    - 直連露天拍賣的超連結

疼痛點摘要:
  🔴 高優先: 搜尋速度、購物車操作、爬蟲進度
  🟡 中優先: 結果可視化、導出功能
  🟢 低優先: 主題切換、偏好設定
```

### 1.3 競品分析

分析類似工具的 UI/UX 優缺點：

```
競品 1: Keepa (Amazon 價格追蹤)
✅ 優點:
  - 清晰的趨勢圖表
  - 簡潔的頂部導航
  - 快速的搜尋建議
❌ 缺點:
  - 色彩單調
  - 功能太多，新手容易迷茫
  - 需要付費才能看到所有功能

競品 2: CamelCamelCamel (Amazon 自動比價)
✅ 優點:
  - 極簡設計，快速上手
  - 一頁就能看完所有信息
  - 價格提醒功能直覺
❌ 缺點:
  - 太簡陋，視覺吸引力低
  - 無法批量操作
  - 不支援複雜搜尋條件

競品 3: 露天拍賣官方網站
✅ 優點:
  - 內容豐富
  - 搜尋功能強大
❌ 缺點:
  - 介面雜亂，廣告多
  - 新手體驗很差
  - 沒有比價功能

結論:
YGO Scraper 應該:
  ✨ 專注核心功能（不要過度設計）
  ✨ 極簡但優雅（不要像露天那樣雜亂）
  ✨ 支援批量操作（區別於手動比價）
  ✨ 清晰的視覺層次（引導使用者完成任務）
```

### 1.4 可用性預期

根據業界標準，定義這個專案的可用性目標：

```
易用性 (Learnability):
  目標: 新使用者 5 分鐘內理解核心功能
  測量: 使用者第一次使用時的困惑點

效率 (Efficiency):
  目標: 搜尋和加入購物車的速度 < 10 秒/張
  測量: 計時使用者完成典型任務

記憶性 (Memorability):
  目標: 使用者一週後不看教學仍能操作
  測量: 使用者回訪率和使用頻率

錯誤防止 (Error Prevention):
  目標: 減少誤操作和資料丟失
  測量: 誤操作導致的撤銷比例

滿足度 (Satisfaction):
  目標: 使用者滿意度 > 80%
  測量: NPS 評分和使用者反饋

可訪問性 (Accessibility):
  目標: WCAG 2.1 AA 等級
  測量: axe 檢查無重大問題
```

### 1.5 可交付物檢查清單

- [ ] 使用者人物誌文檔 (personas.md)
- [ ] 3 個主要使用者旅程地圖
- [ ] 競品分析文檔 (competitive-analysis.md)
- [ ] 可用性評估標準
- [ ] 風險識別和應對方案

---

## 第 2 階段：資訊架構與流程設計
**預計時間**: 2-3 天  
**交付物**: 網站地圖 + 流程圖 + 資訊設計規範

### 2.1 網站地圖 (Sitemap)

從使用者的心理模型出發，組織頁面和功能：

```
YGOscraper (根)
│
├─ 首頁 (Landing/Dashboard)
│  ├─ 新手引導 (只對首次訪客顯示)
│  ├─ 快速搜尋區域
│  ├─ 我的專案列表
│  │  ├─ 最近修改排序
│  │  ├─ 專案卡片 (點擊進入詳情頁)
│  │  └─ 新建專案按鈕
│  └─ 頁腳
│     ├─ 文檔連結
│     ├─ GitHub 連結
│     └─ 回報問題
│
├─ 專案詳情頁 (Project Detail)
│  ├─ 頂部導航
│  │  ├─ 返回首頁
│  │  ├─ 專案名稱
│  │  └─ 快速操作 (編輯、複製、刪除)
│  │
│  ├─ 三欄佈局
│  │  ├─ 左欄：搜尋區域
│  │  │  ├─ 搜尋輸入框
│  │  │  ├─ 快速建議
│  │  │  ├─ 搜尋結果列表
│  │  │  │  ├─ 卡片卡片 (展示圖片、密碼、名稱)
│  │  │  │  └─ 加入購物車按鈕
│  │  │  └─ 分頁或無限捲動
│  │  │
│  │  ├─ 中欄：購物車
│  │  │  ├─ 購物車摘要 (X 張卡, 共 Y 種)
│  │  │  ├─ 卡片列表
│  │  │  │  ├─ 卡片項 (卡名、密碼、數量、CID)
│  │  │  │  ├─ 編輯按鈕 (+-數量)
│  │  │  │  └─ 刪除按鈕
│  │  │  ├─ 清空購物車
│  │  │  ├─ 開始爬蟲按鈕 (主要 CTA)
│  │  │  └─ 爬蟲狀態指示
│  │  │
│  │  └─ 右欄：全域設定
│  │     ├─ 運費設定
│  │     ├─ 最小消費設定
│  │     ├─ 排除關鍵字設定
│  │     ├─ 黑名單設定
│  │     ├─ 進階選項
│  │     └─ 儲存和重置按鈕
│  │
│  └─ 下方：爬蟲進度和結果
│     ├─ 爬蟲進度條 (實時更新)
│     ├─ 進度日誌 (哪些卡片已搜尋)
│     ├─ 結果表格
│     │  ├─ 卡片名稱
│     │  ├─ 推薦賣家
│     │  ├─ 總價
│     │  └─ 展開查看詳細報價
│     ├─ 結果摘要
│     │  ├─ 總成本
│     │  ├─ 預估節省金額
│     │  └─ 推薦訂單
│     └─ 導出選項 (CSV, PDF, 分享)
│
├─ 設定頁面 (Settings)
│  ├─ 全域設定 (跨專案)
│  ├─ 主題設定 (亮色/暗色)
│  ├─ 通知設定
│  ├─ 高級設定
│  │  ├─ API 設定
│  │  └─ 資料管理
│  └─ 關於本應用
│
├─ 文檔頁面 (Docs) - 嵌入應用
│  ├─ 快速開始
│  ├─ 常見問題
│  ├─ API 文檔
│  ├─ 貢獻指南
│  └─ 更新日誌
│
└─ 404 / 錯誤頁面
```

### 2.2 主要流程圖

#### 使用者主流程 (Happy Path)

```
START: 使用者訪問首頁
  ↓
[檢查] 是否首次訪問？
  ├─ YES → 顯示新手引導 → 點擊 "開始使用"
  └─ NO → 直接看首頁
  ↓
[首頁] 顯示最近專案和快速搜尋
  ├─ 選項 A: 點擊「新建專案」→ 建立新專案
  └─ 選項 B: 點擊「快速搜尋」→ 跳到臨時專案
  ↓
[專案詳情頁] 載入專案
  ↓
搜尋卡片 (可重複)
  ├─ 輸入卡片名稱
  ├─ 按 Enter 或點擊搜尋
  ├─ 顯示結果 (1-10 張)
  └─ 點擊「加入購物車」→ 購物車更新 + 提示
  ↓
調整購物車
  ├─ 修改數量
  ├─ 刪除卡片
  └─ 查看摘要
  ↓
[可選] 調整設定
  ├─ 運費、最小消費等
  └─ 儲存
  ↓
點擊「執行爬蟲」
  ├─ 爬蟲開始 → 進度條顯示
  ├─ 實時更新進度
  └─ 完成後顯示結果
  ↓
檢視和導出結果
  ├─ 查看比價表
  ├─ 展開查看詳細報價
  └─ 點擊「導出 CSV」或「分享」
  ↓
END: 前往露天拍賣購買
```

#### 替代流程 (批量輸入)

```
START: 專案詳情頁
  ↓
點擊「批量輸入」
  ↓
[彈窗] 貼上多行卡片名稱
  例: 
  青眼白龍
  增殖的G
  無限泡影
  ↓
點擊「加入購物車」
  ↓
系統逐一搜尋和添加
  ├─ 成功: 購物車計數 +1
  ├─ 失敗: 顯示「未找到」提示
  └─ 進度條顯示進度
  ↓
END: 返回購物車
```

#### 錯誤處理流程

```
場景 1: 搜尋失敗 (無結果)
  ├─ 可能原因: 卡片不存在、名稱錯誤、資料庫未更新
  └─ 處理:
      ├─ 顯示「未找到」提示
      ├─ 建議相似名稱 (搜尋建議)
      └─ 提供「回報資料問題」連結

場景 2: 爬蟲失敗
  ├─ 可能原因: 露天拍賣 API 掛掉、網路問題
  └─ 處理:
      ├─ 顯示詳細錯誤信息
      ├─ 提供「重試」按鈕
      └─ 建議「聯絡支援」連結

場景 3: 購物車超大 (100+ 張卡)
  ├─ 可能原因: 店主大量進貨
  └─ 處理:
      ├─ 警告提示（可能耗時）
      ├─ 提供分批爬蟲選項
      └─ 預估時間提示
```

### 2.3 資訊設計規範

#### 命名規範 (Terminology)

```
應該用的術語          應該避免的術語
─────────────────────────────────────
卡片 (Card)           卡 / 牌
卡片密碼 (Password)   密碼 (容易歧義)
CID (Konami ID)       官方卡號 (歧義)
購物車 (Cart)         籃子 / 手推車
爬蟲 (Scraper)        爬取 / 爬 (太技術)
執行爬蟲 (Run Scraper) 開始爬 (不正式)
比價結果 (Results)    結果 / 報告
推薦方案 (Recommend.) 最優方案
總成本 (Total Cost)   總價 / 花費
```

#### 數據顯示規範

```
金額: 使用千位分隔符
  ✅ 好: NT$1,500
  ❌ 差: NT$1500 / 1500 / $1500

時間: 清晰的相對和絕對時間
  ✅ 好: 修改於 2 小時前 (2026-04-15 14:30)
  ❌ 差: 最後更新: Apr 15

卡片密碼: 使用唯一標識符
  ✅ 好: 95 (密碼) | DABL-JP035 (卡號)
  ❌ 差: 95 / DABL-JP035 (混雜)

數量: 清晰可見
  ✅ 好: [–] 1 [+] 張
  ❌ 差: qty: 1 / 1x

進度: 百分比 + 說明文字
  ✅ 好: 已搜尋 3/10 張卡 (30%)
  ❌ 差: 30% / 進度中...
```

### 2.4 交互設計規範

#### 反饋機制

```
動作             反饋類型            反饋內容            持續時間
──────────────────────────────────────────────────────────────
新增購物車        Toast (彈窗)        ✓ 已加入購物車       2 秒自動關閉
                                    (含卡片名稱)

刪除卡片          確認對話框          「確定刪除?」        用戶操作
                                    [取消] [刪除]

儲存設定          Loading 狀態 +      正在儲存...          自動
              Toast              ✓ 設定已儲存

搜尋              Loading 狀態        搜尋中...            自動
              結果列表            (skeleton)

爬蟲              進度條              已搜尋 5/10          實時更新
                進度日誌            卡片名稱

API 錯誤          Alert 警告框        ❌ 錯誤信息           用戶操作
                建議操作            [重試] [取消]

成功案例          Success Alert       ✓ 爬蟲完成！          3 秒自動
                結果摘要            已找到 XX 報價
```

#### 確認和安全機制

```
高風險操作:
  • 刪除專案 → 強制確認 + 輸入專案名稱確認
  • 清空購物車 → 顯示確認對話框
  • 恢復出廠設定 → 警告提示

中風險操作:
  • 編輯設定 → 簡單確認
  • 更改專案名稱 → 簡單確認

低風險操作:
  • 新增購物車 → 無需確認，只需 Toast 提示
  • 修改數量 → 實時保存，無需確認
```

### 2.5 可交付物檢查清單

- [ ] 完整的網站地圖文檔
- [ ] 主要流程圖 (Figma / draw.io)
- [ ] 替代和錯誤處理流程圖
- [ ] 命名和術語規範文檔
- [ ] 交互和反饋設計指南
- [ ] 資訊架構審查 (與潛在使用者驗證)

---

## 第 3 階段：線框圖與可用性測試
**預計時間**: 4-5 天  
**交付物**: 低保真線框圖 + 可用性測試報告 + 改進方案

### 3.1 工具選擇

根據不同需求推薦：

```
工具          優點                      缺點              適合場景
─────────────────────────────────────────────────────────────
Excalidraw    • 快速、直覺              • 不支援複雜交互   🌟 線框圖(推薦)
              • 開源、免費              • 無元件庫
              • 協作友善

Figma         • 功能完整                • 有學習曲線       線框 + 高保真
              • 強大的元件系統          • 預設模板易重複   (全套流程)
              • 業界標準

Adobe XD      • 直觀的交互設計          • 訂閱制           交互原型
              • 原型功能強              • 相對昂貴

Penpot        • 開源版 Figma            • 生態小           團隊協作

Draw.io       • 簡單快速                • 功能有限         流程圖、圖表
              • 免費
```

**建議**: 用 **Excalidraw 做線框** + **Figma 做高保真** (如果時間允許)

### 3.2 線框圖詳細設計

#### 首頁線框圖 (Desktop)

```
┌──────────────────────────────────────────────────────┐
│ YGO Scraper 🎴        [主題] [文檔] [GitHub] [用戶]    │  Header
├──────────────────────────────────────────────────────┤
│                                                      │
│  🚀 快速開始：搜尋你的第一張卡                        │  Hero
│  [搜尋卡片名稱..............] [搜尋]                  │
│                                                      │
│  需要幫助？[快速教學] [常見問題]                      │
│                                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  📋 我的專案                                         │  Content
│  ┌──────────────┬──────────────┬──────────────┐     │
│  │ 專案 #1      │ 專案 #2      │ 專案 #3      │     │
│  │ 修改: 1h前   │ 修改: 3d 前  │ 修改: 1w 前  │     │
│  │ [開啟]       │ [開啟]       │ [開啟]       │     │
│  └──────────────┴──────────────┴──────────────┘     │
│                                                      │
│  [+ 新建專案]                                        │
│                                                      │
├──────────────────────────────────────────────────────┤
│ 📚 資源                          🤝 社群              │  Footer
│ [快速開始]                       [GitHub]             │
│ [API 文檔]                       [Issues]             │
│ [常見問題]                       [Discussions]        │
│                                                      │
│ © 2026 YGO Scraper | MIT License                    │
└──────────────────────────────────────────────────────┘
```

**設計決策說明**:
- **Hero 區域**: 新用戶能立即明白用途
- **快速搜尋**: 降低入門障礙（不需建專案也能試用）
- **最近專案**: 回訪用戶能快速上手
- **資源明顯**: 開源專案必須清楚引導

#### 專案詳情頁線框圖 (Desktop - 三欄佈局)

```
┌────────────────────────────────────────────────────────────┐
│ ← 專案: 我的卡單 v1    [編輯] [複製] [⋮]                   │
├────────────────────────────────────────────────────────────┤
│                    │                    │                  │
│  左欄:搜尋         │   中欄:購物車      │  右欄:設定        │
│  ──────────        │   ──────────────  │  ────────────   │
│                    │                    │                  │
│  [🔍 搜尋卡片..]   │  🛒 購物車        │  ⚙️ 全域設定      │
│  [搜尋]            │  已加: 3 張        │                  │
│                    │  ─────────────    │  運費:           │
│  搜尋結果:         │  卡片名   | qty    │  [300 ────]    │
│  ┌───────────┐   │  青眼白龍  |[−]1[+]│                  │
│  │ 卡片 1    │   │  增殖的G   |[−]2[+]│  最小消費:        │
│  │ 圖[▭]     │   │  無限泡影  |[−]1[+]│  [1000 ────]   │
│  │ 密:95     │   │  ─────────────    │                  │
│  │ [+ 加購]  │   │                    │  排除詞:         │
│  ├───────────┤   │  [清空] [爬蟲 →]   │  [輸入.......] │
│  │ 卡片 2    │   │                    │                  │
│  │ 圖[▭]     │   │  爬蟲狀態:         │  黑名單:         │
│  │ 密:35     │   │  ⚪ 就緒            │  [輸入.......] │
│  │ [+ 加購]  │   │                    │                  │
│  │...        │   │                    │  [儲存] [重置]  │
│  └───────────┘   │                    │                  │
│                    │                    │                  │
│ [分頁 ❮ 1 2 3 ❯] │                    │                  │
└────────────────────────────────────────────────────────────┘

下方: 爬蟲結果 (根據狀態顯示)

狀態 A: 未執行
┌────────────────────────────────────────────────────────────┐
│ 按上方 [爬蟲] 按鈕開始執行                                   │
└────────────────────────────────────────────────────────────┘

狀態 B: 執行中
┌────────────────────────────────────────────────────────────┐
│ 正在執行爬蟲... [■■■■■───────] 50% (已搜尋 5/10)            │
│ 進度日誌:                                                  │
│ ✓ 青眼白龍 (找到 15 個報價)                               │
│ ✓ 增殖的G (找到 8 個報價)                                 │
│ ⧗ 無限泡影 (搜尋中...)                                     │
│ ○ 其他卡片 (等待中)                                        │
│                                         [取消執行]          │
└────────────────────────────────────────────────────────────┘

狀態 C: 完成
┌────────────────────────────────────────────────────────────┐
│ ✓ 爬蟲完成 (耗時 2 分 30 秒)                                │
│                                                             │
│ 摘要:                                                      │
│ • 已搜尋 10 張卡                                           │
│ • 找到 125 個報價                                          │
│ • 推薦購買方案 (總成本: NT$5,200)                          │
│                                                             │
│ 詳細結果:                                                  │
│ ┌─────────────────────────────────────────────────────┐  │
│ │ 卡片  │ 卡號 │ 推薦賣家 │ 原始 │ 修改 │ 運費 │ 合計   │  │
│ │─────────────────────────────────────────────────────│  │
│ │青眼白龍│ 95  │ 賣家 A  │1500 │  -   │ 300  │1800   │  │
│ │增殖的G │ 35  │ 賣家 A  │ 800 │  -   │ 300  │1100   │  │
│ │...   │ ... │ ...   │ ... │ ... │ ... │ ...   │  │
│ │─────────────────────────────────────────────────────│  │
│ │合計   │     │       │     │     │     │ 5,200 │  │
│ └─────────────────────────────────────────────────────┘  │
│                                                             │
│ [導出 CSV] [分享] [詳細報價]                               │
└────────────────────────────────────────────────────────────┘
```

#### 行動版線框圖 (Mobile 375px)

```
┌──────────────────────┐
│ ← 我的卡單      [⋮]  │ Header
├──────────────────────┤
│                      │
│ 🛒 購物車 (3 張)    │ Quick Summary
│ [展開 ▼]            │
│                      │
├──────────────────────┤
│                      │
│ [🔍 搜尋卡片...] [搜] │ Search
│                      │
├──────────────────────┤
│ 搜尋結果:             │
│ ┌─────────────────┐ │
│ │ 卡片 1          │ │
│ │ 圖[█████]       │ │
│ │ 密: 95          │ │
│ │ [+ 加入購物車] │ │
│ └─────────────────┘ │
│ ┌─────────────────┐ │
│ │ 卡片 2          │ │
│ │ 圖[█████]       │ │
│ │ 密: 35          │ │
│ │ [+ 加入購物車] │ │
│ └─────────────────┘ │
│                      │
│ [← 1  2  3 → ]      │
│                      │
├──────────────────────┤
│ 全域設定 [展開 ▼]   │
│ 爬蟲狀態: ⚪ 就緒    │
│                      │
│ [執行爬蟲]          │
└──────────────────────┘

滑動彈出側邊欄 (購物車和設定)

[購物車] 標籤頁:
┌──────────────────────┐
│ 🛒 購物車            │
│ ─────────────────    │
│ 青眼白龍 (1)         │
│ [−] 1 [+] | [刪除]  │
│ ─────────────────    │
│ 增殖的G (2)          │
│ [−] 2 [+] | [刪除]  │
│ ─────────────────    │
│ 無限泡影 (1)         │
│ [−] 1 [+] | [刪除]  │
│ ─────────────────    │
│ [清空購物車]         │
└──────────────────────┘

[設定] 標籤頁:
┌──────────────────────┐
│ ⚙️ 全域設定          │
│ ─────────────────    │
│ 運費:                │
│ [300 ──────]        │
│ ─────────────────    │
│ 最小消費:            │
│ [1000 ──────]       │
│ ─────────────────    │
│ [儲存]               │
└──────────────────────┘
```

### 3.3 線框圖分析與可用性測試

#### 測試計劃

```
目標: 驗證線框圖的可用性和用戶理解

受測人數: 3-5 人 (符合尼爾森研究)
  • 2 人：卡牌愛好者 (代表小智)
  • 1 人：開發者 (代表大衛)
  • 1-2 人：非目標用戶 (發現盲點)

測試方法: Think-aloud protocol
  • 讓使用者邊操作邊說出想法
  • 不要提供幫助或提示
  • 記錄困惑點和問題

測試任務:

任務 1 (新用戶): 「你想尋找『青眼白龍』和『增殖的G』，
             並找出最便宜的購買方案。」
  預期時間: 2 分鐘
  成功標準: 能完成所有步驟，無重大困惑

任務 2 (回訪用戶): 「你上次搜尋了 3 張卡，
                現在想新增『無限泡影』。」
  預期時間: 30 秒
  成功標準: 能快速找到搜尋框和購物車

任務 3 (高級用戶): 「你想批量導入 20 張卡片，
                並調整爬蟲設定。」
  預期時間: 1.5 分鐘
  成功標準: 清楚操作流程，能找到所有功能

指標測量:
  • Task Completion Rate (任務完成率)
  • Time on Task (完成時間)
  • Errors (使用者犯的錯誤)
  • SUS Score (系統易用性評分)

問卷項目 (SUS):
  1. 我認為我會經常使用此系統
  2. 我認為此系統過於複雜
  3. 我認為此系統易於使用
  4. 我認為需要技術支援才能使用
  5. 此系統的各項功能配合良好
  ...
  (共 10 題，每題 1-5 分)
```

#### 常見可用性問題和解決方案

```
問題 1: 使用者找不到搜尋框
  原因: 搜尋框放在左欄，可能不夠突出
  解決: 
    ✓ 增加搜尋框的視覺權重 (更大、更亮)
    ✓ 添加圖標 (放大鏡)
    ✓ 在首頁也加入搜尋

問題 2: 購物車的「卡片數量」和「已加張數」容易混淆
  原因: 術語不清，「數量」可能指不同含義
  解決:
    ✓ 改用「已加入的卡片類型數」
    ✓ 購物車標題: 「購物車 (3 種卡片, 共 5 張)」

問題 3: 使用者不知道按「爬蟲」後會發生什麼
  原因: 沒有預期設定（耗時、無法取消等）
  解決:
    ✓ 添加「按此開始搜尋價格... 預計 2 分鐘」
    ✓ 顯示進度條和日誌
    ✓ 允許取消

問題 4: 設定面板太複雜，新用戶迷茫
  原因: 太多選項一次顯示
  解決:
    ✓ 預設值設置好 (不需修改也能用)
    ✓ 添加「推薦」標籤
    ✓ 摺疊「進階設定」
    ✓ 每個選項附上說明文字 (?)

問題 5: 行動版本的搜尋結果列表太長
  原因: 卡片卡片內容多，導致版面擁擠
  解決:
    ✓ 簡化卡片設計（只顯示必要信息）
    ✓ 使用卡片高度約 100px (而非 150px)
    ✓ 圖片尺寸縮小或用文字代替
```

### 3.4 迭代改進方案

根據測試結果，製作改進版線框圖：

```
測試前版本 (v1) 問題:
  ❌ 搜尋框太不明顯
  ❌ 購物車術語混亂
  ❌ 設定選項太多

測試後改進 (v2):
  ✅ 搜尋框改為突出位置 + 放大鏡圖標
  ✅ 購物車標題改為「購物車 (3 種卡片, 共 5 張)」
  ✅ 設定項目使用摺疊，只展示基礎設定

測試前預期: 3 分鐘完成任務
測試後實際: 2 分鐘完成任務
改進幅度: ✅ 33% 效率提升
```

### 3.5 可交付物檢查清單

- [ ] 完整的低保真線框圖 (Excalidraw)
  - [ ] 首頁
  - [ ] 專案詳情頁 (Desktop)
  - [ ] 行動版本
  - [ ] 關鍵狀態 (Loading, Error, Success)
- [ ] 可用性測試計劃和問卷
- [ ] 測試記錄 (3+ 使用者的反饋)
- [ ] 可用性測試報告 (包含問題和建議)
- [ ] 迭代改進的線框圖 v2

---

## 第 4 階段：設計系統
**預計時間**: 3-4 天  
**交付物**: 完整的設計系統文檔 + Figma 元件庫

### 4.1 設計系統概述

設計系統是什麼？為什麼需要？

```
定義:
  設計系統是一套可重用的元件、圖案和原則的集合，
  用於建立一致的用戶界面。

為什麼對開源專案重要:
  1. 一致性: 所有頁面和元件看起來和行為一致
  2. 可維護性: 修改設計時，元件庫自動同步
  3. 效率: 新貢獻者無需從零開始設計
  4. 品牌認同: 使用者能認出你的產品
  5. 可訪問性: 統一檢查無障礙標準

案例:
  • Ant Design (阿里巴巴企業級)
  • Material Design (Google)
  • Shopify Polaris
  • GitHub Primer
```

### 4.2 視覺層次和風格定義

#### 風格選擇 (Design Direction)

根據 YGO Scraper 的特性，推薦以下風格：

```
選項 1: 極簡科技風 (Minimalist Tech)
  特點:
    • 大量留白
    • 清晰的線條和邊界
    • 單色為主，點綴一個品牌色
    • 圓角 8px (親和力)
    • 圖標化設計
  適合: 追求效率的開發者
  缺點: 可能過於冷淡，不夠親和

選項 2: 現代卡牌風 (Modern Card-Based)
  特點:
    • 卡片式佈局 (呼應卡牌主題)
    • 漸層背景 (遊戲王卡背靈感)
    • 立體陰影和深度感
    • 紫藍色系 (神秘、科技感)
    • 圓角 12px (溫暖)
  適合: 視覺吸引力和主題契合
  缺點: 可能顯得過度設計

選項 3: 簡約現代風 (Contemporary Minimalism) ⭐ 推薦
  特點:
    • 清晰但不單調
    • 深色背景 (深藍黑)
    • 紫藍色主題色 + 青綠色輔色
    • 圓角 8-12px (平衡)
    • 微妙的漸層和投影
    • 清晰的 icon + 優雅的 typography
  適合: 開源社群 + 易用性 + 視覺吸引力的平衡
  
我們選擇選項 3: 簡約現代風
```

### 4.3 完整的設計系統規範

#### 色彩系統

```
主色板:
┌─────────────────────────────────────────┐
│ Brand Color: Deep Purple                 │
├─────────────────────────────────────────┤
│ #5B21B6 (Dark Purple, 亮度基準)         │
│ #6D28D9 (Slightly lighter)              │
│ #7C3AED (Medium)                        │
│ #8B5CF6 (Light Purple)                  │
│ #A78BFA (Very Light)                    │
│ #DDD6FE (Almost White Purple)           │
└─────────────────────────────────────────┘

輔色:
┌─────────────────────────────────────────┐
│ Secondary: Cyan                          │
│ #06B6D4 (主輔色)                        │
│ #22D3EE (Lighter)                       │
└─────────────────────────────────────────┘

中性色:
┌─────────────────────────────────────────┐
│ 深色模式 (Default - 開源社群常用)        │
│ Background: #0F172A (深藍黑)             │
│ Surface:   #1E293B (深灰藍)              │
│ Surface2:  #334155 (中灰藍)              │
│ Border:    #475569 (淡灰藍)              │
│ Text:      #F1F5F9 (淡灰白)              │
│ TextMuted: #94A3B8 (中灰)               │
│ 
│ 淺色模式 (易訪問性)                      │
│ Background: #FFFFFF (白)                 │
│ Surface:   #F8FAFC (淺灰)               │
│ Surface2:  #F1F5F9 (略深灰)             │
│ Border:    #CBD5E1 (灰)                 │
│ Text:      #0F172A (深灰黑)              │
│ TextMuted: #64748B (中灰)               │
└─────────────────────────────────────────┘

語義色:
┌─────────────────────────────────────────┐
│ Success:   #10B981 (綠)                 │
│ Warning:   #F59E0B (橙)                 │
│ Error:     #EF4444 (紅)                 │
│ Info:      #3B82F6 (藍)                 │
│ 
│ 每個語義色都有浅色變體:
│ Success Light: #ECFDF5                  │
│ Warning Light: #FFFBEB                  │
│ Error Light:   #FEF2F2                  │
│ Info Light:    #EFF6FF                  │
└─────────────────────────────────────────┘

使用規則:
  • 主色 (#5B21B6): 主要按鈕、超連結、焦點狀態
  • 輔色 (#06B6D4): 次要操作、高亮元素
  • 語義色: 只用於狀態指示
  • 中性色: 背景、邊框、文字
```

#### 字體系統

```
Display Font (標題): SF Pro Display (Apple) / Space Grotesk
  用於: H1, 品牌標題
  特性: 現代、幾何、獨特
  
Headline Font: Inter Bold / Plus Jakarta Sans
  用於: H2, H3 (區域標題)
  特性: 清晰、友善、現代
  
Body Font: Inter / System Font (FallBack)
  用於: 正文、標籤、說明
  特性: 高易讀性、中立
  
Mono Font: Fira Code / JetBrains Mono
  用於: 密碼、卡號、代碼塊
  特性: 等寬、易區分

排版規範:
┌──────────────────────────────────────┐
│ H1 頁面標題                           │
│ Size: 32px | Weight: 700 | Line: 1.2 │
│ Margin: 0 0 32px 0                   │
│                                      │
│ H2 區域標題                           │
│ Size: 24px | Weight: 600 | Line: 1.3 │
│ Margin: 24px 0 16px 0                │
│                                      │
│ H3 子標題                             │
│ Size: 18px | Weight: 600 | Line: 1.4 │
│ Margin: 16px 0 12px 0                │
│                                      │
│ Body 正文                             │
│ Size: 14px | Weight: 400 | Line: 1.5 │
│ Margin: 0 0 12px 0                   │
│                                      │
│ Caption 說明文字                       │
│ Size: 12px | Weight: 400 | Line: 1.5 │
│ Color: TextMuted                     │
│                                      │
│ Label 標籤                            │
│ Size: 12px | Weight: 500 | Line: 1.4 │
│ Color: TextMuted                     │
└──────────────────────────────────────┘
```

#### 間距系統

```
8px 為基礎單位的比例系統:

xs  = 4px   (最小間距，字之間)
sm  = 8px   (按鈕內邊距、小元素邊距)
md  = 16px  (元件間距、容器內邊距)
lg  = 24px  (區域間距)
xl  = 32px  (大區域間距)
2xl = 48px  (主要區域分隔)

實例:
Button padding:     sm md        → 8px 16px
Card padding:       lg           → 24px
Section margin:     2xl          → 48px
Element gap:        md           → 16px
Text line-height:   1.5 (21px)   (相對於 14px)
```

#### 圓角系統

```
xs = 4px   (微妙，幾乎看不出)
sm = 6px   (小元素)
md = 8px   (主要元件)
lg = 12px  (卡片、大按鈕)
xl = 16px  (大容器)
full = 9999px (完全圓形，用於圓形頭像)

使用規則:
  Input, Button: md (8px)
  Card, Panel:   lg (12px)
  Badge, Chip:   sm (6px)
  Avatar:        full (圓形)
```

#### 陰影系統

```
Elevation Levels:

Level 0 (無陰影):
  用途: 扁平背景、禁用狀態

Level 1 (微妙):
  Shadow: 0 1px 3px rgba(0, 0, 0, 0.12)
  用途: 普通卡片、輸入框

Level 2 (正常):
  Shadow: 0 4px 8px rgba(0, 0, 0, 0.15)
  用途: 浮動卡片、Hover 狀態

Level 3 (強):
  Shadow: 0 12px 24px rgba(0, 0, 0, 0.20)
  用途: 模態框、Dropdown

Level 4 (最強):
  Shadow: 0 20px 40px rgba(0, 0, 0, 0.25)
  用途: 全頁模態框、重要通知
```

#### 過渡動畫

```
Duration:
  快速:   150ms (微交互、彈窗開啟)
  標準:   200ms (按鈕、焦點)
  慢速:   300ms (頁面轉換)
  深度:   400ms (複雜動畫)

Easing:
  ease-in-out: 標準平滑過渡
  ease-out:    進入時快速
  ease-in:     退出時慢速

實例:
  Button hover:      200ms ease-in-out
  Modal open:        300ms ease-out
  Page transition:   400ms ease-in-out
  Loading spinner:   1000ms linear (循環)
```

### 4.4 元件規範

#### Button (按鈕) - 詳細規範

```
尺寸:
  Small (sm):   32px 高 | 8px 水平 padding
  Medium (md):  40px 高 | 16px 水平 padding (預設)
  Large (lg):   48px 高 | 20px 水平 padding
  
  使用規則:
    sm: 表格中、列表項中的動作
    md: 普通按鈕、表單按鈕
    lg: 主要 CTA (Call-To-Action)

變體:

Primary (主要操作):
  ┌─────────────────┐
  │ 執行爬蟲          │  背景: #5B21B6
  └─────────────────┘  文字: 白
                        邊框: 無
  
  狀態:
  Normal:   #5B21B6
  Hover:    #6D28D9 (加深 +10%)
  Active:   #7C3AED (加深 +20%)
  Disabled: #94A3B8 opacity 50%

Secondary (次要操作):
  ┌─────────────────┐
  │ 取消              │  背景: 透明
  └─────────────────┘  邊框: 2px #5B21B6
                        文字: #5B21B6
  
  狀態:
  Normal:   邊框 #5B21B6, 文字 #5B21B6
  Hover:    背景 #5B21B6 opacity 10%
  Active:   背景 #5B21B6 opacity 20%

Danger (危險操作 - 刪除):
  ┌─────────────────┐
  │ 刪除              │  背景: #EF4444 (紅)
  └─────────────────┘  文字: 白
                        邊框: 無
  
  狀態同 Primary，但使用紅色

Ghost (幽靈按鈕 - 最簡單):
  ┌─────────────────┐
  │ 瞭解詳情          │  背景: 透明
  └─────────────────┘  邊框: 1px #475569
                        文字: #F1F5F9
  
  狀態:
  Normal:   邊框淡，文字正常
  Hover:    邊框亮，背景淡色

Icon Button (圖標按鈕):
  [ ✓ ]              大小: 40px × 40px
                        邊框圓角: md (8px)
  
  狀態:
  Normal:   背景透明，圖標淡灰
  Hover:    背景淡色
  Active:   背景品牌色

規則:
  • 每頁最多一個 Primary Button
  • 確認操作前要明確
  • 危險操作一定是 Danger 變體
  • 使用一致的按鈕大小
  • 按鈕文字要清晰、主動（「搜尋」而非「確定」）
```

#### Input (輸入框)

```
基本樣式:
  ┌─────────────────────────┐
  │ 搜尋卡片名稱...          │
  └─────────────────────────┘
  
  高度: 40px
  邊框: 2px #475569
  圓角: md (8px)
  內邊距: 8px 12px
  字體: 14px, 正常粗細
  文字色: #F1F5F9
  佔位符色: #94A3B8
  背景: #1E293B

狀態:
  Normal:    邊框 #475569
  Focus:     邊框 #5B21B6, 外環光 0 0 0 3px rgba(91, 33, 182, 0.1)
  Error:     邊框 #EF4444, 下方提示紅色文字
  Disabled:  背景 #0F172A, 文字 #475569, 不可聚焦
  Loading:   右側微旋轉 icon

變體:

Search Input (搜尋):
  左邊 icon: 🔍 (放大鏡)
  右邊 icon: [X] 清除 (有內容時出現)

Textarea (多行):
  最小高: 100px
  可調整: 豎向調整大小

Select (下拉):
  右邊 icon: ▼ (下拉箭頭)
  打開時: Dropdown 顯示在下方

Number Input (數字):
  左邊: [−] 減少按鈕
  中間: 數字輸入框
  右邊: [+] 增加按鈕
  例: [−] 1 [+]

規則:
  • 所有 Input 寬度 100% (容器相對)
  • 焦點要有明確視覺反饋
  • 必填欄位用 * 標註
  • 提示文字放在 label 上方或 placeholder 內
  • 錯誤信息清晰，提供解決方案
```

#### Card (卡片)

```
基本樣式:
  ┌─────────────────────────────────┐
  │ 卡片標題                          │
  │                                  │
  │ 卡片內容...                       │
  │                                  │
  │ [按鈕] [按鈕]                     │
  └─────────────────────────────────┘
  
  背景: #1E293B
  邊框: 1px #334155
  圓角: lg (12px)
  內邊距: lg (24px)
  陰影: Level 1
  轉換: 150ms ease-in-out

狀態:
  Normal:    如上
  Hover:     陰影升級到 Level 2, 邊框微亮
  Active:    邊框亮色 (#5B21B6)

變體:

Project Card (專案卡片):
  ┌─────────────────┐
  │ 新專案 #1        │
  │ 修改: 2 小時前  │
  │                │
  │ [開啟] [⋮]     │
  └─────────────────┘
  寬: auto, 最小 200px
  高: auto

Search Result Card (搜尋結果):
  ┌─────────────────┐
  │ [圖片] 卡片名   │
  │        密碼: 95 │
  │ [+ 加入購物車] │
  └─────────────────┘
  寬: 100%, 高: ~120px

Product Card (商品卡片):
  ┌─────────────────────┐
  │ 賣家名稱      價格    │
  │ 原始: 1500   運費300 │
  │ 合計: 1800           │
  │ [加入訂單]          │
  └─────────────────────┘
  寬: auto, 高: auto

規則:
  • 卡片用於分組相關內容
  • Hover 狀態要有反饋
  • 限制卡片最大寬度 (防止過寬)
```

#### Badge (標籤)

```
基本樣式:
  ┌───────┐
  │ 標籤  │  背景: #5B21B6 opacity 20%
  └───────┘  文字: #8B5CF6
             內邊距: 4px 8px
             圓角: full (999px)
             字體: 12px 600 粗

顏色變體:
  Default:  紫色 (上面)
  Success:  綠色 (#10B981)
  Warning:  橙色 (#F59E0B)
  Error:    紅色 (#EF4444)
  Info:     藍色 (#3B82F6)

尺寸:
  Small:   內邊距 2px 6px, 字: 11px
  Medium:  內邊距 4px 8px, 字: 12px (預設)
  Large:   內邊距 6px 12px, 字: 13px

用途:
  • 狀態指示 (「進行中」「已完成」)
  • 分類標籤 (「卡牌」「道具」)
  • 新手提示 (「新功能」「推薦」)
```

#### Alert / Toast

```
Alert (警告框):
  ┌──────────────────────────┐
  │ ⚠️ 標題                   │
  │ 詳細說明文字...           │
  │                          │
  │ [確定] [瞭解詳情]         │
  └──────────────────────────┘
  
  背景: 語義色 light (e.g. Warning Light)
  邊框: 3px 語義色 (e.g. Warning)
  邊框圓角: lg (12px)
  內邊距: lg (24px)

位置: 頁面頂部或相關區域

Toast (提示):
  ┌──────────────────────┐
  │ ✓ 已加入購物車        │
  └──────────────────────┘
  
  背景: Success 色
  文字: 白
  內邊距: sm (8px) md (16px)
  圓角: md (8px)
  陰影: Level 2
  位置: 右下角
  自動消失: 2 秒 (可選)

類型:
  Success:   綠 + ✓
  Error:     紅 + ✗
  Warning:   橙 + ⚠️
  Info:      藍 + ℹ️
```

### 4.5 Figma 設計系統建立

```
Figma 檔案結構:

YGO Scraper Design System (Team Library)
│
├─ 📚 Design System
│  ├─ Color Styles (共 20+ 色彩)
│  ├─ Typography Styles (共 8+ 字體)
│  ├─ Grid & Spacing (8px 基礎)
│  └─ Components
│     ├─ Button (8 變體)
│     │  ├─ Primary/Small
│     │  ├─ Primary/Medium
│     │  ├─ Primary/Large
│     │  ├─ Secondary/*
│     │  ├─ Danger/*
│     │  └─ Ghost/*
│     ├─ Input (5 變體)
│     ├─ Card (3 變體)
│     ├─ Badge (5 色)
│     ├─ Alert
│     ├─ Toast
│     ├─ Modal
│     ├─ Dropdown
│     ├─ Tabs
│     ├─ Pagination
│     ├─ Icon Set (50+ 圖標)
│     └─ Loading States
│
├─ 📄 Pages (設計稿)
│  ├─ Home Page
│  ├─ Project Detail Page
│  ├─ Settings Page
│  ├─ Component Library
│  └─ States & Interactions
│
├─ 🎨 Assets
│  ├─ Logo (各種變體)
│  ├─ Icons (整理分類)
│  ├─ Patterns
│  └─ Illustrations
│
└─ 📋 Guidelines
   ├─ Color Usage
   ├─ Typography Guidelines
   ├─ Spacing Rules
   ├─ Accessibility (A11y)
   └─ Mobile Responsiveness
```

### 4.6 可交付物檢查清單

- [ ] 完整的設計系統文檔 (Markdown)
  - [ ] 色彩系統規範
  - [ ] 字體和排版規範
  - [ ] 間距、圓角、陰影規範
  - [ ] 過渡動畫規範
- [ ] Figma 設計系統檔案
  - [ ] 所有色彩樣式
  - [ ] 所有字體樣式
  - [ ] 完整的元件庫 (最少 15+ 元件)
  - [ ] 各元件的多個狀態變體
- [ ] 元件使用說明書
  - [ ] 每個元件的規格和變體說明
  - [ ] 何時使用哪個元件
  - [ ] 常見誤用和正確做法
- [ ] 無障礙設計檢查清單
  - [ ] 色彩對比度測試
  - [ ] 字體大小最小值
  - [ ] 焦點狀態清晰性

---

## 第 5 階段：高保真設計
**預計時間**: 3-4 天  
**交付物**: 完整的高保真設計稿 (所有頁面和狀態)

### 5.1 設計流程

```
第 1 天: 基礎頁面設計
  • 套用設計系統到線框圖
  • 首頁高保真設計
  • 專案詳情頁高保真設計

第 2 天: 詳細細節和互動狀態
  • 各項輸入狀態 (Normal, Focus, Error)
  • Loading 狀態
  • 成功 / 錯誤狀態
  • Hover 和 Active 狀態

第 3 天: 行動版本設計
  • 響應式設計驗證
  • 行動版本的特殊考慮
  • 觸摸目標大小檢查 (最少 44px)

第 4 天: 微交互和動畫規格
  • 標註過渡時間
  • 標註動畫觸發條件
  • 建立互動原型 (可選)
```

### 5.2 設計驗證清單

```
色彩對比度 (WCAG AA 標準):
  正文文字 vs 背景: 最少 4.5:1
  大標題 vs 背景: 最少 3:1
  圖標 vs 背景: 最少 3:1
  
  檢查工具: Contrast Ratio
  
字體大小:
  正文: 最少 14px
  小文字 (標籤): 最少 12px
  標題: 最少 18px
  
觸摸目標:
  按鈕/可交互元件: 最少 40px × 40px
  目標之間間距: 最少 8px
  
響應式設計:
  Desktop: 1440px+ (16:9)
  Tablet:  768px - 1024px
  Mobile:  375px - 640px
  
  檢查點:
  • 文字是否易讀
  • 按鈕是否易點擊
  • 版面是否平衡
  • 是否有不必要的水平滾動
  
動畫檢查:
  • 動畫是否 > 200ms (感覺自然)
  • 是否有 prefers-reduced-motion 支援
  • 動畫是否有目的 (不是裝飾)
```

### 5.3 可交付物檢查清單

- [ ] 高保真設計稿 (Figma)
  - [ ] 首頁 (Desktop + Mobile)
  - [ ] 專案詳情頁 (Desktop + Mobile)
  - [ ] 所有主要狀態 (Normal, Loading, Error, Success)
  - [ ] 組件變體展示頁
- [ ] 互動原型 (Figma Prototype)
  - [ ] 主要流程的交互
  - [ ] 微交互示範
- [ ] 設計規格文檔
  - [ ] 顏色、字體、間距的確切值
  - [ ] 動畫持續時間和緩動函數
  - [ ] 響應式斷點規則

---

## 第 6 階段：前端架構與開發
**預計時間**: 7-10 天  
**交付物**: 功能完整的前端應用

### 6.1 技術棧選擇和論證

```
選擇 1: React 18 + Vite (現有基礎)
✅ 優點:
  • 你已有現有代碼
  • Vite 速度極快
  • React 18 有最新特性 (Concurrent, Suspense)
  • 社群大，資源多
❌ 缺點:
  • 需要自己管理狀態

選擇 2: Next.js
✅ 優點:
  • 內置 SSR (更好的 SEO)
  • 內置路由和 API
  • 開發體驗好
❌ 缺點:
  • 對於個人專案可能過度工程化
  • 部署複雜性增加

推薦: 保留 React 18 + Vite，但改進架構和狀態管理

補充技術:

狀態管理:
  選項 A: React Context + useReducer (輕量)
  選項 B: Zustand (推薦，簡單強大)
  選項 C: Redux (過度設計)

API 通訊:
  推薦: TanStack Query (React Query)
  優點:
    • 自動快取管理
    • 請求去重
    • 背景同步
    • 樂觀更新支援
    • 開發者工具

UI 框架:
  保持 Tailwind CSS v4
  補充: Headless UI / Radix UI (無樣式元件庫)

表單管理:
  推薦: React Hook Form
  優點:
    • 最小化重新渲染
    • 驗證靈活
    • 檔案大小小

測試框架:
  單元測試: Vitest (比 Jest 快)
  組件測試: React Testing Library
  E2E 測試: Cypress 或 Playwright
```

### 6.2 目錄結構重組

```
frontend/src/
│
├── components/
│   ├── common/                        # 可重用的基礎元件
│   │   ├── Button/
│   │   │   ├── Button.tsx            # 元件代碼
│   │   │   ├── Button.stories.tsx    # Storybook 故事 (可選)
│   │   │   ├── Button.test.tsx       # 單元測試
│   │   │   ├── Button.module.css     # 如果用 CSS Modules
│   │   │   └── index.ts              # 導出
│   │   ├── Card/
│   │   ├── Input/
│   │   ├── Select/
│   │   ├── Modal/
│   │   ├── Toast/
│   │   ├── Badge/
│   │   ├── Icon/
│   │   ├── Skeleton/                # 載入占位符
│   │   └── ...
│   │
│   ├── layout/                        # 佈局元件
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── MainLayout.tsx            # 組合 Header + Sidebar
│   │   ├── AdminLayout.tsx           # 其他佈局
│   │   └── ...
│   │
│   └── features/                      # 功能模組 (業務邏輯)
│       ├── Projects/
│       │   ├── ProjectList/
│       │   │   ├── ProjectList.tsx
│       │   │   ├── ProjectCard.tsx
│       │   │   ├── CreateProjectModal.tsx
│       │   │   └── ProjectList.test.tsx
│       │   ├── ProjectDetail/
│       │   │   ├── ProjectDetail.tsx (頁面容器)
│       │   │   ├── ProjectHeader.tsx
│       │   │   ├── useProjectData.ts (自訂 Hook)
│       │   │   └── ...
│       │   └── index.ts
│       │
│       ├── Cart/
│       │   ├── CartPanel.tsx
│       │   ├── CartItem.tsx
│       │   ├── CartSummary.tsx
│       │   ├── useCart.ts
│       │   └── ...
│       │
│       ├── CardSearch/
│       │   ├── SearchBox.tsx
│       │   ├── SearchResults.tsx
│       │   ├── useCardSearch.ts
│       │   └── ...
│       │
│       ├── Scraper/
│       │   ├── ScraperPanel.tsx
│       │   ├── ProgressBar.tsx
│       │   ├── ResultsTable.tsx
│       │   ├── useScraper.ts
│       │   └── ...
│       │
│       ├── Settings/
│       │   ├── SettingsPanel.tsx
│       │   ├── useSettings.ts
│       │   └── ...
│       │
│       └── ...
│
├── hooks/                            # 自訂 Hooks (邏輯複用)
│   ├── useProjects.ts                # 獲取 / 管理專案
│   ├── useCart.ts                    # 購物車邏輯
│   ├── useScraper.ts                 # 爬蟲控制
│   ├── useCardSearch.ts              # 搜尋邏輯
│   ├── useSettings.ts                # 設定管理
│   ├── useLocalStorage.ts            # 本地存儲
│   └── useAsync.ts                   # 通用異步邏輯
│
├── services/                         # API 層 (後端通訊)
│   ├── api.ts                        # Axios / Fetch 配置
│   ├── projects.service.ts
│   ├── cart.service.ts
│   ├── cards.service.ts
│   ├── scraper.service.ts
│   ├── settings.service.ts
│   └── health.service.ts
│
├── stores/                           # 全域狀態 (Zustand)
│   ├── projectStore.ts
│   ├── cartStore.ts
│   ├── scraperStore.ts
│   ├── settingsStore.ts
│   └── uiStore.ts                    # UI 狀態 (深色模式等)
│
├── types/                            # TypeScript 類型定義
│   ├── index.ts                      # 導出所有類型
│   ├── api.ts                        # API 響應類型
│   ├── models.ts                     # 業務模型類型
│   ├── ui.ts                         # UI 相關類型
│   └── ...
│
├── utils/                            # 工具函數
│   ├── formatting.ts                 # 格式化 (金額、日期)
│   ├── validation.ts                 # 表單驗證
│   ├── constants.ts                  # 常數
│   ├── localStorage.ts               # 本地存儲工具
│   └── ...
│
├── styles/                           # 全域樣式
│   ├── globals.css                   # Tailwind + 全域樣式
│   ├── animations.css                # 動畫定義
│   ├── variables.css                 # CSS 變數
│   └── themes.css                    # 主題 (亮色/暗色)
│
├── pages/                            # 頁面 (路由)
│   ├── HomePage.tsx
│   ├── ProjectDetailPage.tsx
│   ├── SettingsPage.tsx
│   ├── NotFoundPage.tsx
│   └── ...
│
├── App.tsx                           # 主應用程序入口
├── App.css
├── main.tsx                          # Vite 入口
├── index.css                         # Vite 全域樣式
└── vite-env.d.ts                    # Vite 類型定義
```

### 6.3 開發步驟 (優先順序)

#### 階段 1: 基礎設置 (1-2 天)

```
✓ 建立新分支: git checkout -b feat/frontend-redesign

✓ 安裝依賴:
  npm install zustand @tanstack/react-query axios
  npm install -D vitest @vitest/ui @testing-library/react @testing-library/jest-dom

✓ 重組目錄結構
  • 備份舊代碼到 _legacy_backup
  • 建立新目錄
  • 移動必要的檔案

✓ 設置狀態管理 (Zustand):
  // src/stores/projectStore.ts
  import { create } from 'zustand'
  
  interface Project {
    id: string
    name: string
    // ...
  }
  
  export const useProjectStore = create((set) => ({
    projects: [],
    addProject: (project: Project) => set((state) => ({
      projects: [...state.projects, project]
    })),
    // ...
  }))

✓ 設置 API 層:
  // src/services/api.ts
  import axios from 'axios'
  
  export const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
    headers: {
      'Content-Type': 'application/json'
    }
  })

✓ 設置 React Query:
  // src/App.tsx
  import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
  
  const queryClient = new QueryClient()
  
  export default function App() {
    return (
      <QueryClientProvider client={queryClient}>
        {/* App content */}
      </QueryClientProvider>
    )
  }
```

#### 階段 2: 元件庫開發 (2-3 天)

```
優先順序 (由低到高):
1. Button (所有變體)
2. Card
3. Input
4. Badge
5. Alert / Toast
6. Modal
7. Select
8. Pagination

每個元件的檢查清單:
  □ 實現 tsx 檔案
  □ 寫 TypeScript 類型
  □ 單元測試 (至少基本測試)
  □ 支援所有狀態
  □ 支援所有變體
  □ 驗證無障礙屬性 (aria-*)
  □ 響應式測試

例: Button 元件

// src/components/common/Button/Button.tsx
import React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/utils/cn'

const buttonVariants = cva(
  // 基礎樣式
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed',
  {
    variants: {
      variant: {
        primary: 'bg-purple-700 text-white hover:bg-purple-800 active:bg-purple-900',
        secondary: 'border-2 border-purple-700 text-purple-700 hover:bg-purple-700/10',
        danger: 'bg-red-500 text-white hover:bg-red-600',
        ghost: 'border border-slate-500 text-slate-100 hover:bg-slate-700'
      },
      size: {
        sm: 'h-8 px-2 text-sm',
        md: 'h-10 px-4 text-base',
        lg: 'h-12 px-6 text-lg'
      }
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md'
    }
  }
)

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  )
)

Button.displayName = 'Button'

export { Button, buttonVariants }

// src/components/common/Button/Button.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('handles click events', async () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    
    await userEvent.click(screen.getByText('Click'))
    expect(handleClick).toHaveBeenCalled()
  })

  it('disables when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>)
    expect(screen.getByText('Click me')).toBeDisabled()
  })
  
  // ... 更多測試
})
```

#### 階段 3: 佈局和頁面 (2-3 天)

```
優先順序:
1. MainLayout (Header + Sidebar + Main Content)
2. 首頁 (HomePage)
3. 專案詳情頁 (ProjectDetailPage)
4. 設定頁面 (SettingsPage)

例: MainLayout

// src/components/layout/MainLayout.tsx
export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-slate-950">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-700 bg-slate-900">
        <Sidebar />
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col">
        {/* Header */}
        <header className="border-b border-slate-700 bg-slate-900">
          <Header />
        </header>

        {/* Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}

// src/pages/HomePage.tsx
import { useQuery } from '@tanstack/react-query'
import { getProjects } from '@/services/projects.service'
import { MainLayout } from '@/components/layout'
import { ProjectList } from '@/components/features/Projects'

export default function HomePage() {
  const { data: projects, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: getProjects
  })

  if (isLoading) return <MainLayout><Skeleton /></MainLayout>
  if (error) return <MainLayout><ErrorAlert /></MainLayout>

  return (
    <MainLayout>
      <ProjectList projects={projects} />
    </MainLayout>
  )
}
```

#### 階段 4: 核心功能集成 (2-3 天)

```
1. 購物車邏輯 (useCart Hook)
2. 搜尋邏輯 (useCardSearch Hook)
3. 爬蟲控制 (useScraper Hook)
4. 專案詳情頁集成

例: useCart Hook

// src/hooks/useCart.ts
import { useQuery, useMutation } from '@tanstack/react-query'
import { useCartStore } from '@/stores/cartStore'
import { getCart, updateCart } from '@/services/cart.service'

export function useCart(projectId: string) {
  const { cart, addItem, removeItem } = useCartStore()

  const { data, isLoading } = useQuery({
    queryKey: ['cart', projectId],
    queryFn: () => getCart(projectId)
  })

  const updateMutation = useMutation({
    mutationFn: (items) => updateCart(projectId, items),
    onSuccess: () => {
      // 刷新快取或更新本地狀態
    }
  })

  const handleAddItem = async (cardId: string, quantity = 1) => {
    // 樂觀更新
    addItem(cardId, quantity)
    
    // 發送到後端
    await updateMutation.mutateAsync([...cart, { cardId, quantity }])
  }

  return {
    items: data?.items || [],
    isLoading,
    addItem: handleAddItem,
    removeItem,
    updateMutation
  }
}
```

#### 階段 5: 測試和最佳化 (1-2 天)

```
單元測試:
  □ 每個元件至少 5 個測試
  □ 每個 Hook 至少 3 個測試
  □ Services 單元測試

效能最佳化:
  □ 檢查 React DevTools Profiler
  □ 實現 React.memo (避免不必要重新渲染)
  □ 使用 useMemo 和 useCallback
  □ 代碼分割 (路由級別)

無障礙檢查:
  □ 所有互動元件可用鍵盤操作
  □ 焦點指示清晰
  □ 色彩對比度達標
  □ 運行 axe 自動檢查

最佳化檢查清單:
  □ Lighthouse 評分 > 90
  □ 首頁載入時間 < 2s
  □ 沒有未使用的依賴
```

### 6.4 可交付物檢查清單

- [ ] 完整的元件庫
  - [ ] 所有 common/ 元件（最少 10+ 個）
  - [ ] 所有功能元件
  - [ ] 元件型別正確且完整
- [ ] 所有主頁面實現
  - [ ] 首頁
  - [ ] 專案詳情頁
  - [ ] 設定頁面
  - [ ] 錯誤頁面
- [ ] 狀態管理和 API 集成
  - [ ] Zustand stores 完整
  - [ ] 所有 services 實現
  - [ ] React Query 正確配置
- [ ] 測試覆蓋
  - [ ] 單元測試
  - [ ] 集成測試
  - [ ] 無障礙檢查
- [ ] 效能指標
  - [ ] Lighthouse 評分文檔
  - [ ] 載入時間測量

---

## 第 7 階段：測試與最佳化
**預計時間**: 2-3 天  
**交付物**: 測試覆蓋報告 + 效能指標

### 7.1 測試策略

```
測試金字塔:
    ▲
   /|\
  / | \   E2E 測試 (10%)
 /  |  \  • 主要使用者流程
/____|___\ • 跨瀏覽器測試
  /   \
 / | | \  集成測試 (30%)
/  | |  \ • Hook + Component 組合
  /   \
 / | | \ \ 單元測試 (60%)
/___|___|_\ • 元件、Hook、函數

推薦工具組合:
  • Vitest (單元測試，比 Jest 快 10 倍)
  • React Testing Library (元件測試)
  • Playwright (E2E 測試)
```

### 7.2 可訪問性測試

```
自動化測試:
  • axe DevTools (Chrome Extension)
  • Lighthouse (Chrome DevTools)
  • pa11y (CLI)

手動測試:
  • 鍵盤導航 (Tab, Shift+Tab, Enter, Escape)
  • 螢幕閱讀器 (NVDA / JAWS)
  • 色彩對比度檢查

無障礙檢查清單:
  □ WCAG 2.1 AA 等級
  □ 頁面焦點可見和邏輯順序
  □ 所有互動元件可鍵盤操作
  □ 圖像有替代文字
  □ 表單標籤清晰
  □ 動畫無法禁用時無閃爍
  □ 容器的 aria-label 或 aria-labelledby
```

### 7.3 效能最佳化

```
檢查清單:
  □ 首頁 FCP (First Contentful Paint) < 1.5s
  □ LCP (Largest Contentful Paint) < 2.5s
  □ CLS (Cumulative Layout Shift) < 0.1
  □ 沒有 JavaScript 錯誤
  □ 圖片最佳化 (WebP, 正確尺寸)
  □ 代碼分割 (路由級)
  □ 沒有 N+1 查詢

React 特定最佳化:
  □ 實現 React.memo (高頻重新渲染的元件)
  □ 使用 useMemo (昂貴計算)
  □ 使用 useCallback (傳遞給子元件的函數)
  □ 虛擬化長列表 (react-window)
  □ 延遲加載 (React.lazy)
```

### 7.4 可交付物檢查清單

- [ ] 測試覆蓋報告
  - [ ] 單元測試覆蓋 > 80%
  - [ ] 集成測試報告
  - [ ] E2E 測試結果
- [ ] 無障礙檢查報告
  - [ ] axe 檢查零重大問題
  - [ ] 手動測試報告
  - [ ] WCAG 等級報告
- [ ] 效能指標報告
  - [ ] Lighthouse 評分
  - [ ] Core Web Vitals
  - [ ] 載入時間分析

---

## 第 8 階段：文檔與開源準備
**預計時間**: 2-3 天  
**交付物**: 完整的開源文檔 + GitHub 準備

### 8.1 文檔結構

```
docs/
├── CONTRIBUTING.md                  # ⭐ 最重要
│   ├─ 如何設置開發環境
│   ├─ 代碼規範
│   ├─ 提交 PR 流程
│   ├─ UI/UX 貢獻指南
│   └─ 回報 Issue
│
├── DEVELOPMENT.md
│   ├─ 項目結構說明
│   ├─ 開發命令
│   ├─ 常見問題
│   └─ 調試指南
│
├── DESIGN_SYSTEM.md
│   ├─ 設計系統概述
│   ├─ 色彩 / 字體 / 間距規範
│   ├─ 元件清單
│   ├─ 如何添加新元件
│   └─ Figma 連結
│
├── ARCHITECTURE.md
│   ├─ 前端架構圖
│   ├─ 目錄結構說明
│   ├─ 狀態管理流程
│   ├─ API 通訊模式
│   └─ 資料流圖
│
├── API_REFERENCE.md (自動生成)
│   ├─ 所有 API 端點
│   ├─ 請求 / 響應範例
│   └─ 錯誤代碼
│
├── DESIGN_DECISIONS.md
│   └─ 重要決策的原因
│
├── CHANGELOG.md
│   └─ 版本歷史
│
└── FAQ.md
    └─ 常見問題
```

### 8.2 可交付物檢查清單

- [ ] 完整的文檔集
  - [ ] CONTRIBUTING.md
  - [ ] DEVELOPMENT.md
  - [ ] DESIGN_SYSTEM.md
  - [ ] ARCHITECTURE.md
  - [ ] API_REFERENCE.md
  - [ ] CHANGELOG.md
  - [ ] FAQ.md
- [ ] GitHub 設置
  - [ ] 更新 README.md
  - [ ] 設置 Issue 樣板
  - [ ] 設置 PR 樣板
  - [ ] 設置 Discussion
  - [ ] 添加貢獻指南連結
- [ ] 準備發布
  - [ ] 設置版本號 (Semantic Versioning)
  - [ ] 建立 Release Notes
  - [ ] 準備演示影片 (可選)

---

## 學習成果清單

完成本計劃後，你將掌握：

### 🎨 UI/UX 設計
- ✅ 完整的 UX 設計流程（研究 → 設計 → 測試 → 開發）
- ✅ 線框圖和原型製作
- ✅ 可用性測試方法和指標
- ✅ 設計系統建立和維護
- ✅ 高保真設計和互動規格
- ✅ 無障礙設計 (WCAG)

### 🏗️ 前端架構
- ✅ 大規模 React 應用的目錄結構
- ✅ 狀態管理最佳實踐 (Zustand)
- ✅ API 層和服務分層
- ✅ 自訂 Hook 的設計
- ✅ 測試策略和實踐
- ✅ 效能最佳化技巧

### 🚀 開源貢獻
- ✅ 如何設計社群友善的代碼
- ✅ 文檔編寫和維護
- ✅ GitHub 工作流和 PR 審查
- ✅ 貢獻指南編寫
- ✅ 社群管理基礎

### 💡 業界標準和最佳實踐
- ✅ 設計思維和用戶中心設計
- ✅ 敏捷開發流程
- ✅ 代碼審查和品質控制
- ✅ 版本管理和語義版本控制

---

## 時間表總結

| 階段 | 預計時間 | 關鍵交付物 |
|------|---------|---------|
| 第 1 階段：策略與研究 | 3-4 天 | 使用者人物誌 + 競品分析 |
| 第 2 階段：資訊架構 | 2-3 天 | 網站地圖 + 流程圖 |
| 第 3 階段：線框圖與測試 | 4-5 天 | 線框圖 + 測試報告 |
| 第 4 階段：設計系統 | 3-4 天 | 設計系統文檔 + Figma |
| 第 5 階段：高保真設計 | 3-4 天 | 完整設計稿 |
| 第 6 階段：前端開發 | 7-10 天 | 功能完整的應用 |
| 第 7 階段：測試與最佳化 | 2-3 天 | 測試報告 + 效能指標 |
| 第 8 階段：文檔與開源 | 2-3 天 | 完整文檔 + GitHub 準備 |
| **總計** | **26-36 天** | **可發布的開源應用** |

**如果時間緊張**，可以平行進行（第 5 + 6 並行），縮短為 3-4 週。

---

## 推薦的工具和資源

### 設計工具
- **Figma** (https://figma.com) - 免費方案足夠個人專案
- **Excalidraw** (https://excalidraw.com) - 開源線框圖
- **Contrast Ratio** (https://www.contrastchecker.com) - 色彩對比度檢查

### 開發工具
- **VS Code** - 代碼編輯器
- **Chrome DevTools** - 調試和效能檢查
- **Lighthouse** - 效能和無障礙測試
- **axe DevTools** - 無障礙自動檢查

### 學習資源
- **Interaction Design Foundation** (https://www.interaction-design.org) - 免費 UX 課程
- **Nielsen Norman Group** - UX 研究文章
- **WebAIM** - 無障礙設計資源
- **Material Design** - 設計系統參考
- **React 官方文檔** - React 最佳實踐

---

## 現在該開始了！

### 下一步行動

1. **確認時間承諾**
   - 你能每週投入多少小時？
   - 目標完成時間？

2. **建立 GitHub 里程碑**
   - 為每個階段建立 GitHub Issues
   - 標記優先級和預計時間

3. **準備工作區**
   - 新建分支：`git checkout -b feat/frontend-redesign`
   - 建立 `/docs` 目錄保存設計文檔

4. **從第 1 階段開始**
   - 建立 `docs/personas.md` 文檔
   - 開始編寫使用者人物誌

### 我能幫你什麼？

- **設計階段** (1-5): 我可以幫你製作線框圖、設計系統、提供設計反饋
- **開發階段** (6): 我可以幫你審核代碼、優化架構、解決技術問題
- **文檔階段** (7-8): 我可以幫你編寫和整理文檔
- **全程**: 我可以作為你的 UX/前端顧問，提供指導和反饋

**建議的合作方式**：
- 每個階段完成後，拿著交付物來與我討論
- 遇到設計問題時，我幫你分析和優化
- 開發時，我幫你審查代碼品質和架構

---

**讓我們開始吧！你想從哪個階段開始？** 🚀
