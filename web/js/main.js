const { createApp, ref, reactive, onMounted, computed, watch, nextTick } = Vue;

const app = createApp({
    setup() {
        // State
        const activeTab = ref('projects');
        const projectList = ref([]);
        const currentProject = ref(null);
        const selectedProject = ref('');
        const loading = ref(false);
        const isRunning = ref(false);
        const logContent = ref('');
        const resultsData = ref(null);
        const activeSellers = ref([]); // For accordion

        const cartData = reactive({
            global_settings: {
                default_shipping_cost: 60,
                min_purchase_limit: 0,
                global_exclude_keywords: [],
                global_exclude_seller: []
            },
            shopping_cart: []
        });
        
        const currentProjectName = computed(() => {
            if (!currentProject.value) return '';
            // Handle both Windows and Unix paths
            const parts = currentProject.value.split(/[/\\]/);
            return parts[parts.length - 1];
        });

        // Initialize
        onMounted(async () => {
            await refreshProjects();
            // Expose log function to Eel
            window.eel.expose(appendLog, 'appendLog');
        });

        // UI State for Global Tags
        const inputVisibleKeywords = ref(false);
        const inputValueKeywords = ref('');
        const keywordInputRef = ref(null);

        const inputVisibleSellers = ref(false);
        const inputValueSellers = ref('');
        const sellerInputRef = ref(null);

        // Methods
        async function refreshProjects() {
            loading.value = true;
            try {
                projectList.value = await eel.get_project_list()();
            } catch (e) {
                console.error("Failed to load projects", e);
                ElementPlus.ElMessage.error('無法載入專案列表');
            } finally {
                loading.value = false;
            }
        }

        async function createProject() {
            loading.value = true;
            try {
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

        async function loadProject() {
            if (!selectedProject.value) return;
            loading.value = true;
            try {
                const path = await eel.load_project(selectedProject.value)();
                if (path) {
                    currentProject.value = path;
                    ElementPlus.ElMessage.success(`已載入: ${selectedProject.value}`);
                    await loadCart();
                    await loadResults(); // Try to load existing results
                    activeTab.value = 'cart';
                }
            } catch (e) {
                ElementPlus.ElMessage.error('載入失敗');
            } finally {
                loading.value = false;
            }
        }

        async function loadCart() {
            if (!currentProject.value) return;
            try {
                const data = await eel.read_cart_json(currentProject.value)();
                
                // Merge data to preserve reactivity and ensure defaults
                cartData.global_settings = {
                    default_shipping_cost: 60,
                    min_purchase_limit: 0,
                    global_exclude_keywords: [],
                    global_exclude_seller: [],
                    ...data.global_settings
                };
                
                // Process cart items to add UI state for tags
                const items = data.shopping_cart || [];
                cartData.shopping_cart = items.map(item => ({
                    ...item,
                    target_ids: item.target_ids || [],
                    // UI states
                    ui_inputVisible: false,
                    ui_inputValue: ''
                }));
                
            } catch (e) {
                console.error(e);
            }
        }

        function addCartItem() {
            cartData.shopping_cart.push({
                card_name_zh: '新卡片',
                required_amount: 3,
                target_ids: [],
                ui_inputVisible: false,
                ui_inputValue: ''
            });
        }

        function removeCartItem(index) {
            cartData.shopping_cart.splice(index, 1);
        }

        // --- Tag Handling Logic ---

        // Generic close handler
        const handleClose = (list, tag) => {
            list.splice(list.indexOf(tag), 1);
        }

        // Global Keywords
        const showInputKeywords = () => {
            inputVisibleKeywords.value = true;
            nextTick(() => {
                if(keywordInputRef.value) keywordInputRef.value.input.focus();
            });
        }

        const handleInputConfirmKeywords = () => {
            if (inputValueKeywords.value) {
                if (!cartData.global_settings.global_exclude_keywords.includes(inputValueKeywords.value)) {
                    cartData.global_settings.global_exclude_keywords.push(inputValueKeywords.value);
                }
            }
            inputVisibleKeywords.value = false;
            inputValueKeywords.value = '';
        }

        // Global Sellers
        const showInputSellers = () => {
            inputVisibleSellers.value = true;
            nextTick(() => {
                if(sellerInputRef.value) sellerInputRef.value.input.focus();
            });
        }

        const handleInputConfirmSellers = () => {
            if (inputValueSellers.value) {
                if (!cartData.global_settings.global_exclude_seller.includes(inputValueSellers.value)) {
                    cartData.global_settings.global_exclude_seller.push(inputValueSellers.value);
                }
            }
            inputVisibleSellers.value = false;
            inputValueSellers.value = '';
        }

        // Cart Item IDs (Per Item)
        const showInputItem = (item, index) => {
            item.ui_inputVisible = true;
            nextTick(() => {
                // Access dynamic ref using ID or class could be tricky, 
                // but Vue allows refs in v-for. We will use a function ref in template or just rely on standard focus if possible.
                // Simpler: use document.getElementById since we can generate unique IDs
                const el = document.getElementById(`save-tag-input-${index}`);
                if(el) el.focus();
            });
        }

        const handleInputConfirmItem = (item) => {
            if (item.ui_inputValue) {
                const val = item.ui_inputValue.trim().toUpperCase();
                if (val && !item.target_ids.includes(val)) {
                    item.target_ids.push(val);
                }
            }
            item.ui_inputVisible = false;
            item.ui_inputValue = '';
        }

        // --- End Tag Handling ---

        async function saveAndRun() {
            if (!currentProject.value) return;
            
            // Prepare clean data (strip UI props)
            const cleanData = {
                global_settings: JSON.parse(JSON.stringify(cartData.global_settings)),
                shopping_cart: cartData.shopping_cart.map(item => ({
                    card_name_zh: item.card_name_zh,
                    required_amount: item.required_amount,
                    target_ids: item.target_ids
                }))
            };

            isRunning.value = true;
            logContent.value = 'Initializing...\n';
            
            try {
                // 1. Save
                await eel.save_cart_json(currentProject.value, cleanData)();
                ElementPlus.ElMessage.success('設定已儲存');
                
                // 2. Run
                const success = await eel.run_full_process(currentProject.value)();
                if (success) {
                    ElementPlus.ElMessage.success('計算完成！請查看結果分頁');
                    await loadResults();
                    // Optional: auto switch?
                    // activeTab.value = 'results'; 
                } else {
                    ElementPlus.ElMessage.error('執行過程發生錯誤');
                }
            } catch (e) {
                ElementPlus.ElMessage.error('執行失敗: ' + e);
            } finally {
                isRunning.value = false;
            }
        }

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

        function getTabTitle(tab) {
            const map = {
                'projects': '專案管理 (Project Management)',
                'cart': '購物車配置 (Configuration)',
                'results': '計算結果 (Optimization Results)'
            };
            return map[tab] || 'Dashboard';
        }

        // Exposed to Eel
        function appendLog(msg) {
            logContent.value += msg + '\n';
            // Auto scroll
            nextTick(() => {
                const term = document.querySelector('.terminal-window');
                if (term) term.scrollTop = term.scrollHeight;
            });
        }

        // Return bindings
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
            
            // Refs for Inputs
            inputVisibleKeywords,
            inputValueKeywords,
            keywordInputRef,
            inputVisibleSellers,
            inputValueSellers,
            sellerInputRef,

            // Methods
            createProject,
            loadProject,
            addCartItem,
            removeCartItem,
            saveAndRun,
            loadResults,
            getTabTitle,
            
            // Tag Methods
            handleClose,
            showInputKeywords,
            handleInputConfirmKeywords,
            showInputSellers,
            handleInputConfirmSellers,
            showInputItem,
            handleInputConfirmItem
        };
    }
});

// Register Icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}

app.use(ElementPlus);
app.mount('#app');