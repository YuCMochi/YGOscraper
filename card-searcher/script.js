const searchInput = document.getElementById('search-input');
const searchButton = document.getElementById('search-button');
const resultsContainer = document.getElementById('results-container');
const loadingStatus = document.getElementById('loading-status');
// 新增購物車相關元素
const cartContainer = document.getElementById('cart-container');
const cartItemsList = document.getElementById('cart-items');
const cartTotalSpan = document.getElementById('cart-total');
const optimizeButton = document.getElementById('optimize-button');
const optimizeOutput = document.getElementById('optimize-output');


let cardData = [];
let db = null;
let shoppingCart = {}; // 初始化購物車物件 { cardName: quantity }

// Function to dynamically load a script
function loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.async = true; // 異步載入
        script.onload = resolve; // 載入成功時 resolve Promise
        script.onerror = reject; // 載入失敗時 reject Promise
        document.head.appendChild(script); // 將 script 加到 head
    });
}

// --- 資料載入 (使用 sql.js with dynamic loading) ---
async function loadCardData() {
    loadingStatus.textContent = '正在載入 SQL.js 函式庫...';
    try {
        // 0. 動態載入 sql.js 並等待完成
        await loadScript('https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.10.3/sql-wasm.js');
        // 到這裡表示 sql.js 腳本已載入

        // 檢查 initSqlJs 是否真的被定義了
        if (typeof initSqlJs === 'undefined') {
            throw new Error("initSqlJs 函數未定義。請檢查 sql.js 是否成功載入。");
        }

        loadingStatus.textContent = '正在初始化 SQL.js...';

        // 1. 初始化 sql.js Wasm 模組
        const SQL = await initSqlJs({
            locateFile: file => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.10.3/${file}`
        });

        // --- 後續邏輯不變 ---
        loadingStatus.textContent = '正在下載資料庫檔案 (cards.cdb)...';
        const response = await fetch('cards.cdb');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const fileBuffer = await response.arrayBuffer();

        loadingStatus.textContent = '正在載入資料庫...';
        db = new SQL.Database(new Uint8Array(fileBuffer));

        loadingStatus.textContent = '正在查詢卡片資料...';
        const results = db.exec("SELECT id, name, desc FROM texts");

        if (results.length > 0 && results[0].values) {
            const columns = results[0].columns;
            cardData = results[0].values.map(row => {
                let card = {};
                columns.forEach((col, index) => {
                    card[col] = row[index];
                });
                return card;
            });
            console.log(`成功從資料庫載入 ${cardData.length} 筆卡片資料。`);
            loadingStatus.textContent = `資料庫載入完成 (${cardData.length} 筆卡片)。`;
            searchButton.textContent = '搜尋';
            searchButton.disabled = false;
        } else {
            console.warn("texts 表查詢無結果，嘗試查詢 datas 表...");
            const dataResults = db.exec("SELECT id FROM datas");
             if (dataResults.length > 0 && dataResults[0].values) {
                 throw new Error("資料庫 texts 表無結果，無法獲取卡片名稱。");
             } else {
                throw new Error("資料庫查詢無結果或格式錯誤 (texts 和 datas 表均無有效資料)。");
             }
        }

    } catch (error) {
        console.error("無法載入或查詢卡片資料庫:", error);
        loadingStatus.textContent = '';
        resultsContainer.innerHTML = `<p style="color: red;">錯誤：無法載入卡片資料庫 (cards.cdb)。請確認檔案存在、網路連線正常且資料庫結構正確。錯誤訊息: ${error.message}</p>`;
        searchButton.textContent = '載入失敗';
        searchButton.disabled = true;
    }
}

// --- 搜尋邏輯 (修改後) ---
function performSearch() {
    const query = searchInput.value.trim().toLowerCase();
    resultsContainer.innerHTML = ''; // 清空之前的結果

    if (!query) {
        return;
    }

    if (!db || cardData.length === 0) {
        resultsContainer.innerHTML = '<p>卡片資料尚未載入或載入失敗。</p>';
        return;
    }

    // 1. 篩選出所有名稱包含 query 的卡片
    const filteredCards = cardData.filter(card =>
        card.name && card.name.toLowerCase().includes(query)
    );

    // 2. 將篩選結果按卡片名稱分組
    const groupedResults = filteredCards.reduce((groups, card) => {
        const name = card.name; // 使用卡片名稱作為分組的 key
        if (!groups[name]) {
            groups[name] = []; // 如果這個名稱的分組還不存在，就建立一個空陣列
        }
        groups[name].push(card); // 將卡片加入對應名稱的分組
        return groups;
    }, {}); // 初始值是一個空物件

    // 3. 將分組後的結果傳遞給 displayResults
    //    我們傳遞物件的值 (也就是每個名稱對應的卡片陣列)
    displayResults(Object.values(groupedResults));
}

// --- 結果顯示 (修改後) ---
// 參數 'groups' 現在是一個陣列，每個元素是包含同名卡片的陣列
function displayResults(groups) {
    resultsContainer.innerHTML = ''; // 清空之前的結果 (移到 performSearch 開頭)
    if (groups.length === 0) {
        resultsContainer.innerHTML = '<p>找不到符合條件的卡片。</p>';
        return;
    }

    groups.forEach(cardGroup => {
        if (cardGroup.length === 0) return;

        const firstCard = cardGroup[0];
        const cardName = firstCard.name; // 卡片名稱用於購物車

        const cardElement = document.createElement('div');
        cardElement.classList.add('card-result');

        const nameElement = document.createElement('h3');
        nameElement.textContent = cardName;
        cardElement.appendChild(nameElement);

        const imageContainer = document.createElement('div');
        imageContainer.classList.add('card-image-container');

        cardGroup.forEach(card => {
            const img = document.createElement('img');
            img.src = `https://salix5.github.io/query-data/pics/${card.id}.jpg`;
            img.alt = `${cardName} (ID: ${card.id})`;
            img.title = `ID: ${card.id}`;
            img.onerror = function() {
                this.alt = '圖片載入失敗';
                this.style.display = 'none';
                console.warn(`無法載入圖片: ${this.src}`);
            };
            imageContainer.appendChild(img);
        });

        cardElement.appendChild(imageContainer);

        const descElement = document.createElement('p');
        descElement.textContent = firstCard.desc ? firstCard.desc.replace(/\\n/g, '\n') : '（無效果描述）';
        cardElement.appendChild(descElement);

        // 新增加入購物車按鈕
        const addButton = document.createElement('button');
        addButton.classList.add('add-to-cart-button');
        addButton.textContent = '加入購物車';
        addButton.onclick = () => addToCart(cardName); // 點擊時呼叫 addToCart
        cardElement.appendChild(addButton);


        resultsContainer.appendChild(cardElement);
    });
}

// --- 新增購物車相關函數 ---

// 加入購物車
function addToCart(cardName) {
    if (shoppingCart[cardName]) {
        shoppingCart[cardName]++;
    } else {
        shoppingCart[cardName] = 1;
    }
    updateCartDisplay();
    console.log("購物車:", shoppingCart); // 調試用
}

// 更改數量
function changeQuantity(cardName, change) {
    if (shoppingCart[cardName]) {
        shoppingCart[cardName] += change;
        if (shoppingCart[cardName] <= 0) {
            delete shoppingCart[cardName]; // 數量小於等於 0 時移除
        }
        updateCartDisplay();
    }
}

// 從購物車移除
function removeFromCart(cardName) {
    if (shoppingCart[cardName]) {
        delete shoppingCart[cardName];
        updateCartDisplay();
    }
}

// 更新購物車顯示
function updateCartDisplay() {
    cartItemsList.innerHTML = ''; // 清空現有列表
    let totalItems = 0;

    for (const cardName in shoppingCart) {
        const quantity = shoppingCart[cardName];
        totalItems += quantity;

        const listItem = document.createElement('li');

        const nameSpan = document.createElement('span');
        nameSpan.textContent = `${cardName} x ${quantity}`;

        const controlsDiv = document.createElement('div');
        controlsDiv.classList.add('cart-item-controls');

        const decreaseButton = document.createElement('button');
        decreaseButton.textContent = '-';
        decreaseButton.onclick = () => changeQuantity(cardName, -1);

        const increaseButton = document.createElement('button');
        increaseButton.textContent = '+';
        increaseButton.onclick = () => changeQuantity(cardName, 1);

        const removeButton = document.createElement('button');
        removeButton.textContent = '移除';
        removeButton.style.color = 'red';
        removeButton.onclick = () => removeFromCart(cardName);

        controlsDiv.appendChild(decreaseButton);
        controlsDiv.appendChild(increaseButton);
        controlsDiv.appendChild(removeButton);

        listItem.appendChild(nameSpan);
        listItem.appendChild(controlsDiv);
        cartItemsList.appendChild(listItem);
    }

    cartTotalSpan.textContent = totalItems;
    // 只有購物車有東西時才顯示購物車區塊和按鈕
    cartContainer.style.display = totalItems > 0 ? 'block' : 'none';
}


// --- 事件監聽器 ---
searchButton.addEventListener('click', performSearch);
searchInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        performSearch();
    }
});

// 修改 optimizeButton 的事件監聽器
optimizeButton.addEventListener('click', () => {
    if (Object.keys(shoppingCart).length === 0) {
        alert("購物車是空的！請先加入卡片。");
        optimizeOutput.textContent = "購物車是空的。";
        optimizeOutput.style.display = 'block';
        return;
    }

    // 1. 將 shoppingCart 物件轉換為 JSON 字串
    const cartJsonString = JSON.stringify(shoppingCart, null, 2); // null, 2 用於美化輸出

    // 2. 建立 Blob 物件
    const blob = new Blob([cartJsonString], { type: 'application/json' });

    // 3. 建立下載連結
    const downloadLink = document.createElement('a');
    downloadLink.href = URL.createObjectURL(blob);
    downloadLink.download = 'cart.json'; // 設定下載的檔名

    // 4. 觸發點擊以下載檔案
    document.body.appendChild(downloadLink); // 需要先加到 DOM 才能觸發 click
    downloadLink.click();

    // 5. 清理
    document.body.removeChild(downloadLink);
    URL.revokeObjectURL(downloadLink.href); // 釋放 URL 物件

    // 更新提示訊息
    optimizeOutput.textContent = `cart.json 已產生並開始下載。\n請將下載的 cart.json 檔案移動到 card-searcher 目錄下，然後執行 main_controller.py。`;
    optimizeOutput.style.display = 'block';

    // 注意：這裡不再直接呼叫後端，而是提示用戶手動操作
});


// --- 初始化 ---
loadCardData(); // 頁面載入時開始載入資料庫
updateCartDisplay(); // 初始化購物車顯示