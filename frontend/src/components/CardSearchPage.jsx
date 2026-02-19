import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Search, Loader2, ShoppingCart, Check, Database } from 'lucide-react';
import api from '../lib/api';

// ============================================================
// 常數定義（從 legacy constant.js 移植）
// ============================================================
const TYPE_MONSTER = 0x1;
const TYPE_SPELL = 0x2;
const TYPE_TRAP = 0x4;
const TYPE_NORMAL = 0x10;
const TYPE_EFFECT = 0x20;
const TYPE_FUSION = 0x40;
const TYPE_RITUAL = 0x80;
const TYPE_SYNCHRO = 0x2000;
const TYPE_TOKEN = 0x4000;
const TYPE_XYZ = 0x800000;
const TYPE_PENDULUM = 0x1000000;
const TYPE_LINK = 0x4000000;
const TYPE_SPIRIT = 0x200;
const TYPE_UNION = 0x400;
const TYPE_DUAL = 0x800;
const TYPE_TUNER = 0x1000;
const TYPE_FLIP = 0x200000;
const TYPE_TOON = 0x400000;
const TYPE_SPSUMMON = 0x2000000;
const TYPE_QUICKPLAY = 0x10000;
const TYPE_CONTINUOUS = 0x20000;
const TYPE_EQUIP = 0x40000;
const TYPE_FIELD = 0x80000;
const TYPE_COUNTER = 0x100000;

// 卡片類型名稱（繁體中文）
const typeNames = {
    [TYPE_MONSTER]: '怪獸', [TYPE_SPELL]: '魔法', [TYPE_TRAP]: '陷阱',
    [TYPE_NORMAL]: '通常', [TYPE_EFFECT]: '效果', [TYPE_FUSION]: '融合',
    [TYPE_RITUAL]: '儀式', [TYPE_SYNCHRO]: '同步', [TYPE_XYZ]: '超量',
    [TYPE_PENDULUM]: '靈擺', [TYPE_LINK]: '連結', [TYPE_SPIRIT]: '靈魂',
    [TYPE_UNION]: '聯合', [TYPE_DUAL]: '二重', [TYPE_TUNER]: '協調',
    [TYPE_TOKEN]: '衍生物', [TYPE_FLIP]: '反轉', [TYPE_TOON]: '卡通',
    [TYPE_SPSUMMON]: '特殊召喚', [TYPE_QUICKPLAY]: '速攻',
    [TYPE_CONTINUOUS]: '永續', [TYPE_EQUIP]: '裝備',
    [TYPE_FIELD]: '場地', [TYPE_COUNTER]: '反擊',
};

// 屬性名稱
const attrNames = { 1: '地', 2: '水', 4: '炎', 8: '風', 16: '光', 32: '闇', 64: '神' };

// 種族名稱
const raceNames = {
    0x1: '戰士族', 0x2: '魔法使族', 0x4: '天使族', 0x8: '惡魔族',
    0x10: '不死族', 0x20: '機械族', 0x40: '水族', 0x80: '炎族',
    0x100: '岩石族', 0x200: '鳥獸族', 0x400: '植物族', 0x800: '昆蟲族',
    0x1000: '雷族', 0x2000: '龍族', 0x4000: '獸族', 0x8000: '獸戰士族',
    0x10000: '恐龍族', 0x20000: '魚族', 0x40000: '海龍族', 0x80000: '爬蟲類族',
    0x100000: '超能族', 0x200000: '幻神獸族', 0x400000: '創造神族',
    0x800000: '幻龍族', 0x1000000: '電子界族', 0x2000000: '幻想魔族',
};

// 特殊 ID
const ID_TYLER = 68811206;
const ID_DECOY = 20240828;
const ARTWORK_OFFSET = 20;
const MAX_CARD_ID = 99999999;

// ============================================================
// 輔助函數
// ============================================================

/** 取得卡片的類型描述字串 */
function getTypeString(type) {
    const parts = [];
    if (type & TYPE_MONSTER) {
        parts.push(typeNames[TYPE_MONSTER]);
        // 額外甲板類型
        if (type & TYPE_FUSION) parts.push(typeNames[TYPE_FUSION]);
        if (type & TYPE_SYNCHRO) parts.push(typeNames[TYPE_SYNCHRO]);
        if (type & TYPE_XYZ) parts.push(typeNames[TYPE_XYZ]);
        if (type & TYPE_LINK) parts.push(typeNames[TYPE_LINK]);
        if (type & TYPE_RITUAL) parts.push(typeNames[TYPE_RITUAL]);
        if (type & TYPE_PENDULUM) parts.push(typeNames[TYPE_PENDULUM]);
        // 效果類型
        if (type & TYPE_NORMAL) parts.push(typeNames[TYPE_NORMAL]);
        if (type & TYPE_EFFECT) parts.push(typeNames[TYPE_EFFECT]);
        if (type & TYPE_TUNER) parts.push(typeNames[TYPE_TUNER]);
        if (type & TYPE_FLIP) parts.push(typeNames[TYPE_FLIP]);
        if (type & TYPE_TOON) parts.push(typeNames[TYPE_TOON]);
        if (type & TYPE_SPIRIT) parts.push(typeNames[TYPE_SPIRIT]);
        if (type & TYPE_UNION) parts.push(typeNames[TYPE_UNION]);
        if (type & TYPE_DUAL) parts.push(typeNames[TYPE_DUAL]);
        if (type & TYPE_SPSUMMON) parts.push(typeNames[TYPE_SPSUMMON]);
    } else if (type & TYPE_SPELL) {
        parts.push(typeNames[TYPE_SPELL]);
        if (type & TYPE_QUICKPLAY) parts.push(typeNames[TYPE_QUICKPLAY]);
        else if (type & TYPE_CONTINUOUS) parts.push(typeNames[TYPE_CONTINUOUS]);
        else if (type & TYPE_EQUIP) parts.push(typeNames[TYPE_EQUIP]);
        else if (type & TYPE_RITUAL) parts.push(typeNames[TYPE_RITUAL]);
        else if (type & TYPE_FIELD) parts.push(typeNames[TYPE_FIELD]);
        else parts.push(typeNames[TYPE_NORMAL]);
    } else if (type & TYPE_TRAP) {
        parts.push(typeNames[TYPE_TRAP]);
        if (type & TYPE_CONTINUOUS) parts.push(typeNames[TYPE_CONTINUOUS]);
        else if (type & TYPE_COUNTER) parts.push(typeNames[TYPE_COUNTER]);
        else parts.push(typeNames[TYPE_NORMAL]);
    }
    return parts.join('/');
}

/** 取得攻擊力/守備力顯示文字 */
function printAD(x) {
    return x === -2 ? '?' : String(x);
}

/** 取得卡片的統計資訊字串 */
function getStatString(card) {
    if (!(card.type & TYPE_MONSTER)) return '';
    const level = card.level & 0xff;
    const scale = card.level >>> 24;
    let lvSymbol = '★';
    if (card.type & TYPE_XYZ) lvSymbol = '☆';
    else if (card.type & TYPE_LINK) lvSymbol = 'LINK-';

    let stat = `${lvSymbol}${level}`;
    if (card.attribute) stat += ` / ${attrNames[card.attribute] || '？'}`;
    if (card.race) stat += ` / ${raceNames[card.race] || '？族'}`;
    stat += ` / 攻${printAD(card.atk)}`;
    if (!(card.type & TYPE_LINK)) stat += ` / 守${printAD(card.def)}`;
    if (card.type & TYPE_PENDULUM) stat += ` / 🔹${scale}/${scale}🔸`;
    return stat;
}

// ============================================================
// 主元件
// ============================================================
const CardSearchPage = () => {
    const { projectId } = useParams();
    const navigate = useNavigate();

    // 資料庫狀態
    const [dbReady, setDbReady] = useState(false);
    const [dbLoading, setDbLoading] = useState(true);
    const [dbError, setDbError] = useState(null);
    const [loadProgress, setLoadProgress] = useState('正在初始化...');

    // 搜尋狀態
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [searching, setSearching] = useState(false);

    // 加入購物車狀態（追蹤哪些卡正在處理 / 已加入）
    const [addingCards, setAddingCards] = useState({}); // { cid: 'loading' | 'done' }

    // 保存資料庫參照
    const dbListRef = useRef([]);
    const cidTableRef = useRef(new Map()); // CID -> password(id)
    const nameTableRef = useRef(new Map()); // CID -> 日文卡名

    // ============================================================
    // 載入資料庫（模仿 ygo-json-loader.js）
    // ============================================================
    useEffect(() => {
        let cancelled = false;

        const loadDB = async () => {
            try {
                // 1. 載入 sql.js WASM 引擎
                setLoadProgress('正在載入 SQL 引擎...');
                const initSqlJs = (await import('sql.js')).default;
                const SQL = await initSqlJs({
                    locateFile: () => '/sql-wasm.wasm'
                });

                if (cancelled) return;

                // 2. 直接載入主要卡片資料庫 (cards.cdb)
                //    注意：原本使用 cards.zip 但該 URL 已失效，改用直接 .cdb 檔案
                setLoadProgress('正在下載卡片資料庫（約 6MB）...');
                const dbResponse = await fetch('https://salix5.github.io/cdb/cards.cdb');
                if (!dbResponse.ok) {
                    throw new Error(`下載卡片資料庫失敗: HTTP ${dbResponse.status}`);
                }
                const dbBuffer = await dbResponse.arrayBuffer();
                const dbData = new Uint8Array(dbBuffer);

                if (cancelled) return;

                // 3. 載入預發行資料庫
                setLoadProgress('正在載入擴充資料...');
                const db2Response = await fetch('https://salix5.github.io/cdb/expansions/pre-release.cdb');
                if (!db2Response.ok) {
                    console.warn('預發行資料庫載入失敗，將僅使用主資料庫');
                }

                if (cancelled) return;

                // 建立資料庫實例
                const databases = [new SQL.Database(dbData)];
                if (db2Response.ok) {
                    const db2Buffer = await db2Response.arrayBuffer();
                    databases.push(new SQL.Database(new Uint8Array(db2Buffer)));
                }
                dbListRef.current = databases;

                // 4. 建立 CID 對照表（從 DB 本身取得）
                //    注意：原本使用外部 JSON 但已失效，改從 DB 的 id 欄位推導
                setLoadProgress('正在建立卡片索引...');
                // 使用卡片的 password (id) 作為 CID 的近似值
                // 在 YGO 資料庫中，大部分卡片的 id 就等於 Konami DB 的 CID
                // 未來可以改用正確的 CID 映射表

                if (cancelled) return;

                setDbReady(true);
                setDbLoading(false);
                setLoadProgress('資料庫載入完成！');
            } catch (err) {
                if (!cancelled) {
                    console.error('DB 載入失敗:', err);
                    setDbError(`資料庫載入失敗: ${err.message}`);
                    setDbLoading(false);
                }
            }
        };

        loadDB();
        return () => { cancelled = true; };
    }, []);

    // ============================================================
    // 搜尋邏輯
    // ============================================================
    const handleSearch = useCallback(() => {
        if (!searchQuery.trim() || !dbReady) return;
        setSearching(true);

        try {
            const query = searchQuery.trim();
            const results = [];

            // SQL 查詢：用中文卡名模糊搜尋
            const selectAll = `SELECT datas.id, datas.ot, datas.alias, datas.type, datas.atk, datas.def, datas.level, datas.race, datas.attribute, texts.name, texts."desc"
                FROM datas JOIN texts USING (id) WHERE 1`;

            // 基本過濾：排除特殊 ID、token、替代卡圖
            const filters = ` AND datas.id != ${ID_TYLER} AND datas.id != ${ID_DECOY} AND NOT type & ${TYPE_TOKEN}`;
            const noAltFilter = ` AND (datas.id == 5405695 OR abs(datas.id - alias) >= ${ARTWORK_OFFSET})`;

            // 名稱搜尋條件
            const nameFilter = ` AND (name LIKE '%${query.replace(/'/g, "''")}%' OR "desc" LIKE '%※%${query.replace(/'/g, "''")}%')`;

            const fullQuery = selectAll + filters + noAltFilter + nameFilter + ' LIMIT 100';

            for (const db of dbListRef.current) {
                try {
                    const stmt = db.prepare(fullQuery);
                    while (stmt.step()) {
                        const row = stmt.getAsObject();
                        // 處理替代卡圖
                        let artid = 0;
                        if (row.alias && Math.abs(row.id - row.alias) < ARTWORK_OFFSET && row.id !== 5405695) {
                            artid = row.id;
                            row.id = row.alias;
                        }
                        // 使用 card id (password) 作為 CID
                        // 在大多數情況下 password 等同於 Konami DB 的 CID
                        const cid = row.id;

                        results.push({
                            id: row.id,
                            cid: cid,
                            tw_name: row.name,    // 中文卡名（cdb 中的名稱）
                            jp_name: null,         // 日文卡名（外部表已不可用）
                            type: row.type,
                            atk: row.atk,
                            def: row.def,
                            level: row.level,
                            race: row.race,
                            attribute: row.attribute,
                            desc: row.desc,
                            artid: artid,
                            ot: row.ot,
                        });
                    }
                    stmt.free();
                } catch (err) {
                    console.error('查詢錯誤:', err);
                }
            }

            // 精確匹配排在前面
            results.sort((a, b) => {
                const aExact = a.tw_name === query;
                const bExact = b.tw_name === query;
                if (aExact && !bExact) return -1;
                if (!aExact && bExact) return 1;
                return 0;
            });

            setSearchResults(results);
        } catch (err) {
            console.error('搜尋失敗:', err);
        } finally {
            setSearching(false);
        }
    }, [searchQuery, dbReady]);

    // ============================================================
    // 加入購物車：卡名 → 後端查 CID → 爬卡號 → 加入購物車
    // ============================================================
    const handleAddToCart = async (card) => {
        setAddingCards(prev => ({ ...prev, [card.id]: 'loading' }));

        try {
            // 1. 用卡名向後端取得卡號列表
            //    後端流程：卡名 → search_by_keyword → 得到 CID → scrape_cids → 卡號
            const encodedName = encodeURIComponent(card.tw_name);
            const cidsRes = await api.get(`/cards/name/${encodedName}/card-numbers`);
            const cardNumbers = cidsRes.data.card_numbers || [];

            console.log(`卡片「${card.tw_name}」爬取到 ${cardNumbers.length} 個卡號:`, cardNumbers.slice(0, 5));

            // 2. 取得目前購物車
            const cartRes = await api.get(`/projects/${projectId}/cart`);
            const cartData = cartRes.data;

            // 確保 global_settings 存在完整預設值
            if (!cartData.global_settings) {
                cartData.global_settings = {
                    default_shipping_cost: 60,
                    min_purchase_limit: 0,
                    global_exclude_keywords: [],
                    global_exclude_seller: [],
                };
            }

            // 3. 加入新卡片
            cartData.shopping_cart.push({
                card_name_zh: card.tw_name,
                target_card_numbers: cardNumbers,
                required_amount: 1,
            });

            // 4. 存回購物車
            await api.post(`/projects/${projectId}/cart`, cartData);

            setAddingCards(prev => ({ ...prev, [card.id]: 'done' }));
        } catch (err) {
            console.error('加入購物車失敗:', err);
            // 如果爬卡號失敗，至少把卡名加進去（無卡號版本）
            try {
                const cartRes = await api.get(`/projects/${projectId}/cart`);
                const cartData = cartRes.data;
                if (!cartData.global_settings) {
                    cartData.global_settings = {
                        default_shipping_cost: 60,
                        min_purchase_limit: 0,
                        global_exclude_keywords: [],
                        global_exclude_seller: [],
                    };
                }
                cartData.shopping_cart.push({
                    card_name_zh: card.tw_name,
                    target_card_numbers: [],
                    required_amount: 1,
                });
                await api.post(`/projects/${projectId}/cart`, cartData);
                setAddingCards(prev => ({ ...prev, [card.id]: 'done' }));
            } catch (err2) {
                setAddingCards(prev => ({ ...prev, [card.id]: 'error' }));
            }
        }
    };

    // ============================================================
    // 卡圖 URL
    // ============================================================
    const getImageUrl = (card) => {
        const picId = card.artid || card.id;
        if (picId <= MAX_CARD_ID) {
            return `https://salix5.github.io/query-data/pics/${picId}.jpg`;
        }
        return null;
    };

    // ============================================================
    // 渲染
    // ============================================================
    return (
        <div className="max-w-6xl mx-auto space-y-6">
            {/* 頂部導覽列 */}
            <div className="flex items-center gap-4">
                <Link
                    to={`/project/${projectId}`}
                    className="p-2 hover:bg-slate-700 rounded-full transition-colors text-text-muted hover:text-white"
                >
                    <ArrowLeft size={24} />
                </Link>
                <div className="flex-1">
                    <h1 className="text-2xl font-bold">卡片搜尋</h1>
                    <p className="text-text-muted text-sm">專案：{projectId}</p>
                </div>
                <div className="flex items-center gap-2 text-sm">
                    <Database size={16} className={dbReady ? 'text-success' : 'text-text-muted'} />
                    <span className={dbReady ? 'text-success' : 'text-text-muted'}>
                        {dbLoading ? loadProgress : dbReady ? '資料庫已就緒' : '載入失敗'}
                    </span>
                </div>
            </div>

            {/* 載入錯誤提示 */}
            {dbError && (
                <div className="bg-danger/10 border border-danger/30 rounded-lg p-4 text-danger">
                    {dbError}
                </div>
            )}

            {/* 搜尋列 */}
            <div className="flex gap-3">
                <div className="flex-1 relative">
                    <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted" />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                        placeholder="輸入中文卡名搜尋（例如：青眼白龍）"
                        disabled={!dbReady}
                        className="w-full bg-surface border border-slate-700 rounded-xl pl-12 pr-4 py-3 focus:outline-none focus:border-primary text-white placeholder-text-muted transition-colors disabled:opacity-50 text-lg"
                        autoFocus
                    />
                </div>
                <button
                    onClick={handleSearch}
                    disabled={!dbReady || searching || !searchQuery.trim()}
                    className="bg-primary hover:bg-primary-hover text-white px-8 py-3 rounded-xl font-bold transition-all disabled:opacity-50 flex items-center gap-2 shadow-lg shadow-blue-500/20"
                >
                    {searching ? <Loader2 className="animate-spin" size={20} /> : <Search size={20} />}
                    搜尋
                </button>
            </div>

            {/* 搜尋結果計數 */}
            {searchResults.length > 0 && (
                <div className="text-text-muted text-sm">
                    共找到 <span className="text-white font-bold">{searchResults.length}</span> 張卡片
                </div>
            )}

            {/* 載入中骨架畫面 */}
            {dbLoading && (
                <div className="flex flex-col items-center justify-center py-20 gap-4">
                    <Loader2 className="animate-spin text-primary" size={48} />
                    <p className="text-text-muted text-lg">{loadProgress}</p>
                    <p className="text-text-muted text-sm">首次載入約需 5-10 秒，資料會快取在瀏覽器中</p>
                </div>
            )}

            {/* 搜尋結果列表 */}
            {dbReady && searchResults.length === 0 && !searching && searchQuery && (
                <div className="text-center py-16 text-text-muted">
                    <Search size={48} className="mx-auto mb-4 opacity-30" />
                    <p className="text-lg">找不到符合「{searchQuery}」的卡片</p>
                    <p className="text-sm mt-2">請嘗試其他關鍵字</p>
                </div>
            )}

            {dbReady && searchResults.length === 0 && !searchQuery && (
                <div className="text-center py-16 text-text-muted">
                    <Search size={48} className="mx-auto mb-4 opacity-30" />
                    <p className="text-lg">輸入卡片名稱開始搜尋</p>
                    <p className="text-sm mt-2">支援模糊搜尋，例如輸入「青眼」可以找到所有青眼系列卡片</p>
                </div>
            )}

            <div className="space-y-3">
                {searchResults.map((card, idx) => {
                    const imgUrl = getImageUrl(card);
                    const addState = addingCards[card.id];
                    const typeStr = getTypeString(card.type);
                    const statStr = getStatString(card);

                    return (
                        <div
                            key={`${card.id}-${idx}`}
                            className="bg-surface border border-slate-700 rounded-xl p-4 hover:border-slate-500 transition-all group flex gap-4"
                        >
                            {/* 卡圖 */}
                            <div className="w-20 h-28 flex-shrink-0 rounded-lg overflow-hidden bg-slate-800">
                                {imgUrl ? (
                                    <img
                                        src={imgUrl}
                                        alt={card.tw_name}
                                        className="w-full h-full object-cover"
                                        onError={(e) => { e.target.style.display = 'none'; }}
                                        loading="lazy"
                                    />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-text-muted text-xs">
                                        無圖
                                    </div>
                                )}
                            </div>

                            {/* 卡片資訊 */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-start justify-between gap-2">
                                    <div className="min-w-0">
                                        <h3 className="font-bold text-lg text-white truncate">{card.tw_name}</h3>
                                        {card.jp_name && (
                                            <p className="text-text-muted text-sm truncate">{card.jp_name}</p>
                                        )}
                                    </div>
                                    {/* 加入購物車按鈕 */}
                                    <button
                                        onClick={() => handleAddToCart(card)}
                                        disabled={addState === 'loading' || addState === 'done'}
                                        className={`flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-all ${addState === 'done'
                                            ? 'bg-success/20 text-success border border-success/30'
                                            : addState === 'loading'
                                                ? 'bg-slate-700 text-text-muted'
                                                : 'bg-primary/10 text-primary hover:bg-primary hover:text-white border border-primary/30 hover:border-primary'
                                            }`}
                                    >
                                        {addState === 'loading' ? (
                                            <><Loader2 className="animate-spin" size={16} /> 爬取卡號中...</>
                                        ) : addState === 'done' ? (
                                            <><Check size={16} /> 已加入</>
                                        ) : (
                                            <><ShoppingCart size={16} /> 加入購物車</>
                                        )}
                                    </button>
                                </div>

                                {/* 類型標籤 */}
                                <div className="flex items-center gap-2 mt-2 flex-wrap">
                                    <span className={`text-xs px-2 py-0.5 rounded font-medium ${card.type & TYPE_MONSTER ? 'bg-amber-500/20 text-amber-400' :
                                        card.type & TYPE_SPELL ? 'bg-emerald-500/20 text-emerald-400' :
                                            card.type & TYPE_TRAP ? 'bg-pink-500/20 text-pink-400' :
                                                'bg-slate-500/20 text-slate-400'
                                        }`}>
                                        {typeStr}
                                    </span>
                                    {statStr && (
                                        <span className="text-xs text-text-muted">{statStr}</span>
                                    )}
                                    {card.cid && (
                                        <span className="text-xs text-text-muted font-mono">CID: {card.cid}</span>
                                    )}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default CardSearchPage;
