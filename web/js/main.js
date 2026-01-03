const { createApp, ref, reactive, onMounted, computed, watch, nextTick } = Vue;

const app = createApp({
    setup() {
        // --- 狀態定義 (State) ---
        const activeTab = ref('projects');          // 當前選中的標籤頁 (專案、購物車、結果)
        const projectList = ref([]);               // 所有的專案列表
        const currentProject = ref(null);          // 當前啟用的專案路徑
        const selectedProject = ref('');           // 下拉選單中選中的專案名稱
        const loading = ref(false);                // 是否正在載入中
        const isRunning = ref(false);              // 是否正在執行計算程序
        const logContent = ref('');                // 終端機日誌內容
        const resultsData = ref(null);             // 計算後的結果數據
        const activeSellers = ref([]);             // 用於結果頁面的手風琴展開狀態

        // 購物車數據模型
        const cartData = reactive({
            global_settings: {
                default_shipping_cost: 60,         // 預設運費
                min_purchase_limit: 0,             // 最低購買限制
                global_exclude_keywords: [],       // 全域排除關鍵字
                global_exclude_seller: []          // 全域排除賣家
            },
            shopping_cart: []                      // 購物車內的卡片清單
        });
        
        // 計算當前專案的名稱 (從路徑中擷取最後一段)
        const currentProjectName = computed(() => {
            if (!currentProject.value) return '';
            // 處理 Windows (\) 與 Unix (/) 的路徑分隔符
            const parts = currentProject.value.split(/[/\\]/);
            return parts[parts.length - 1];
        });

        // --- 初始化 (Initialize) ---
        onMounted(async () => {
            // 組件掛載後重新整理專案列表
            await refreshProjects();
            // 將 appendLog 函數暴露給 Eel (讓 Python 端的程式可以呼叫它來更新 UI)
            window.eel.expose(appendLog, 'appendLog');
        });

        // --- 全域標籤 (Global Tags) 的 UI 狀態 ---
        const inputVisibleKeywords = ref(false);    // 排除關鍵字輸入框是否顯示
        const inputValueKeywords = ref('');         // 排除關鍵字輸入框的值
        const keywordInputRef = ref(null);          // 排除關鍵字輸入框的 DOM 引用

        const inputVisibleSellers = ref(false);     // 排除賣家輸入框是否顯示
        const inputValueSellers = ref('');          // 排除賣家輸入框的值
        const sellerInputRef = ref(null);           // 排除賣家輸入框的 DOM 引用

        // --- 核心方法 (Methods) ---

        // 重新整理專案列表
        async function refreshProjects() {
            loading.value = true;
            try {
                // 呼叫 Python 端獲取專案清單
                projectList.value = await eel.get_project_list()();
            } catch (e) {
                console.error("Failed to load projects", e);
                ElementPlus.ElMessage.error('無法載入專案列表');
            } finally {
                loading.value = false;
            }
        }

        // 建立新專案
        async function createProject() {
            loading.value = true;
            try {
                // 呼叫 Python 端建立專案，成功會回傳新專案路徑
                const newPath = await eel.create_new_project()();
                if (newPath) {
                    ElementPlus.ElMessage.success('專案建立成功');
                    await refreshProjects();
                    currentProject.value = newPath;
                    await loadCart();
                    activeTab.value = 'cart';
                }
            } catch (e) {
                ElementPlus.ElMessage.error('建立失敗: ' + e);
            } finally {
                loading.value = false;
            }
        }

        // 載入選中的專案
        async function loadProject() {
            if (!selectedProject.value) return;
            loading.value = true;
            try {
                // 呼叫 Python 端載入指定的專案
                const path = await eel.load_project(selectedProject.value)();
                if (path) {
                    currentProject.value = path;
                    ElementPlus.ElMessage.success(`已載入: ${selectedProject.value}`);
                    await loadCart();
                    await loadResults(); // 嘗試載入已存在的計算結果
                    activeTab.value = 'cart';
                }
            } catch (e) {
                ElementPlus.ElMessage.error('載入失敗');
            } finally {
                loading.value = false;
            }
        }

        // 讀取購物車 JSON 檔案
        async function loadCart() {
            if (!currentProject.value) return;
            try {
                const data = await eel.read_cart_json(currentProject.value)();
                
                // 合併數據以保持響應性並確保預設值存在
                cartData.global_settings = {
                    default_shipping_cost: 60,
                    min_purchase_limit: 0,
                    global_exclude_keywords: [],
                    global_exclude_seller: [],
                    ...data.global_settings
                };
                
                // 處理購物車項目，加入 UI 用的標籤輸入狀態
                const items = data.shopping_cart || [];
                cartData.shopping_cart = items.map(item => ({
                    ...item,
                    target_card_numbers: item.target_card_numbers || [],
                    ui_inputVisible: false,
                    ui_inputValue: ''
                }));
                
            } catch (e) {
                console.error(e);
            }
        }

        // 手動新增一個空的購物車項目
        function addCartItem() {
            cartData.shopping_cart.push({
                card_name_zh: '新卡片',
                required_amount: 1,
                target_card_numbers: [],
                ui_inputVisible: false,
                ui_inputValue: ''
            });
        }

        // 移除購物車項目
        function removeCartItem(index) {
            cartData.shopping_cart.splice(index, 1);
        }

        // --- 標籤處理邏輯 (Tag Handling Logic) ---

        // 通用的標籤關閉 (移除) 處理器
        const handleClose = (list, tag) => {
            list.splice(list.indexOf(tag), 1);
        }

        // 顯示全域關鍵字輸入框
        const showInputKeywords = () => {
            inputVisibleKeywords.value = true;
            nextTick(() => {
                if(keywordInputRef.value) keywordInputRef.value.input.focus();
            });
        }

        // 確認新增全域關鍵字
        const handleInputConfirmKeywords = () => {
            if (inputValueKeywords.value) {
                if (!cartData.global_settings.global_exclude_keywords.includes(inputValueKeywords.value)) {
                    cartData.global_settings.global_exclude_keywords.push(inputValueKeywords.value);
                }
            }
            inputVisibleKeywords.value = false;
            inputValueKeywords.value = '';
        }

        // 顯示全域排除賣家輸入框
        const showInputSellers = () => {
            inputVisibleSellers.value = true;
            nextTick(() => {
                if(sellerInputRef.value) sellerInputRef.value.input.focus();
            });
        }

        // 確認新增全域排除賣家
        const handleInputConfirmSellers = () => {
            if (inputValueSellers.value) {
                if (!cartData.global_settings.global_exclude_seller.includes(inputValueSellers.value)) {
                    cartData.global_settings.global_exclude_seller.push(inputValueSellers.value);
                }
            }
            inputVisibleSellers.value = false;
            inputValueSellers.value = '';
        }

        // 顯示特定卡片的編號輸入框
        const showInputItem = (item, index) => {
            item.ui_inputVisible = true;
            nextTick(() => {
                // 使用唯一 ID 來聚焦到輸入框
                const el = document.getElementById(`save-tag-input-${index}`);
                if(el) el.focus();
            });
        }

        // 確認新增特定卡片的編號
        const handleInputConfirmItem = (item) => {
            if (item.ui_inputValue) {
                const val = item.ui_inputValue.trim().toUpperCase();
                if (val && !item.target_card_numbers.includes(val)) {
                    item.target_card_numbers.push(val);
                }
            }
            item.ui_inputVisible = false;
            item.ui_inputValue = '';
        }

        // --- 搜尋模組整合 (Search/Query Module Integration) ---
        
        // 開啟卡片搜尋視窗
        function openSearch() {
            window.open('query_module/index.html', 'CardSearch', 'width=1000,height=800');
        }

        // 監聽來自搜尋視窗 (iframe/popup) 的訊息
        window.addEventListener('message', async (event) => {
            if (event.data && event.data.type === 'ADD_CARD') {
                const { cid, name, id } = event.data;
                console.log("Received card:", name, cid, id);
                
                if (!cid) {
                     ElementPlus.ElMessage.warning(`此卡片 (${name}) 無法對應到 Konami ID (CID)`);
                     return;
                }

                try {
                    // 呼叫 Python 端從 Konami 資料庫抓取卡片各版本的詳細資料
                    const versions = await eel.fetch_card_details(cid)();
                    
                    if (versions && versions.length > 0) {
                        // 提取所有卡片編號
                        const cardNumbers = versions.map(v => v.card_number).filter(n => n);
                        // 去除重複編號
                        const uniqueNumbers = [...new Set(cardNumbers)];

                        if (uniqueNumbers.length > 0) {
                             cartData.shopping_cart.push({
                                card_name_zh: name,
                                required_amount: 1,
                                target_card_numbers: uniqueNumbers,
                                ui_inputVisible: false,
                                ui_inputValue: ''
                            });
                            ElementPlus.ElMessage.success(`已加入卡片: ${name} (找到 ${uniqueNumbers.length} 種版本)`);
                        } else {
                            ElementPlus.ElMessage.warning(`找到卡片 ${name} 但無有效編號`);
                        }
                    } else {
                        ElementPlus.ElMessage.warning(`無法從 Konami 資料庫抓取到 ${name} (CID: ${cid}) 的詳細資料`);
                         // 備案：只加入名稱，讓使用者手動填寫編號
                         cartData.shopping_cart.push({
                                card_name_zh: name,
                                required_amount: 1,
                                target_card_numbers: [],
                                ui_inputVisible: false,
                                ui_inputValue: ''
                            });
                    }

                } catch (e) {
                    console.error("Error processing card add:", e);
                    ElementPlus.ElMessage.error("加入卡片時發生錯誤");
                }
            }
        });

        // --- 儲存與執行 ---

        async function saveAndRun() {
            if (!currentProject.value) return;
            
            // 準備乾淨的數據 (移除 UI 用的暫時屬性)
            const cleanData = {
                global_settings: JSON.parse(JSON.stringify(cartData.global_settings)),
                shopping_cart: cartData.shopping_cart.map(item => ({
                    card_name_zh: item.card_name_zh,
                    required_amount: item.required_amount,
                    target_card_numbers: item.target_card_numbers
                }))
            };

            isRunning.value = true;
            logContent.value = '正在初始化...\n';
            
            try {
                // 1. 儲存設定到 JSON
                await eel.save_cart_json(currentProject.value, cleanData)();
                ElementPlus.ElMessage.success('設定已儲存');
                
                // 2. 執行完整計算流程
                const success = await eel.run_full_process(currentProject.value)();
                if (success) {
                    ElementPlus.ElMessage.success('計算完成！請查看結果分頁');
                    await loadResults();
                } else {
                    ElementPlus.ElMessage.error('執行過程發生錯誤');
                }
            } catch (e) {
                ElementPlus.ElMessage.error('執行失敗: ' + e);
            } finally {
                isRunning.value = false;
            }
        }

        // 載入計算結果
        async function loadResults() {
            if (!currentProject.value) return;
            try {
                const res = await eel.get_results(currentProject.value)();
                if (res && !res.error) {
                    resultsData.value = res;
                } else {
                    resultsData.value = null;
                }
            } catch (e) {
                resultsData.value = null;
            }
        }

        // 獲取標籤頁標題
        function getTabTitle(tab) {
            const map = {
                'projects': '專案管理 (Project Management)',
                'cart': '購物車配置 (Configuration)',
                'results': '計算結果 (Optimization Results)'
            };
            return map[tab] || 'Dashboard';
        }

        // 暴露給 Eel 使用：附加日誌訊息到終端機視窗
        function appendLog(msg) {
            logContent.value += msg + '\n';
            // 自動捲動到底部
            nextTick(() => {
                const term = document.querySelector('.terminal-window');
                if (term) term.scrollTop = term.scrollHeight;
            });
        }

        // 回傳給 Template 使用的狀態與方法
        return {
            activeTab,
            projectList,
            currentProject,
            currentProjectName,
            selectedProject,
            loading,
            isRunning,
            logContent,
            cartData,
            resultsData,
            activeSellers,
            
            // 輸入框引用
            inputVisibleKeywords,
            inputValueKeywords,
            keywordInputRef,
            inputVisibleSellers,
            inputValueSellers,
            sellerInputRef,

            // 方法
            createProject,
            loadProject,
            addCartItem,
            removeCartItem,
            saveAndRun,
            loadResults,
            getTabTitle,
            
            // 標籤處理方法
            handleClose,
            showInputKeywords,
            handleInputConfirmKeywords,
            showInputSellers,
            handleInputConfirmSellers,
            showInputItem,
            handleInputConfirmItem,
            openSearch
        };
    }
});

// 註冊 Element Plus 圖示
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}

app.use(ElementPlus);
app.mount('#app');