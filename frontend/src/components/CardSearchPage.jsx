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

    // ============================================================
    // 初始化設定
    // ============================================================
    useEffect(() => {
        setDbReady(true);
        setDbLoading(false);
    }, []);

    // ============================================================
    // 搜尋邏輯
    // ============================================================
    const handleSearch = useCallback(async () => {
        if (!searchQuery.trim() || !dbReady) return;
        setSearching(true);

        try {
            const query = searchQuery.trim();
            // 後端將返回 [{passcode, name, cid, type, atk, def, level, race, attribute, desc, image_url}]
            const response = await api.get(`/cards/search?q=${encodeURIComponent(query)}`);

            // 將後端回傳資料轉換為原件預期的格式
            const mappedResults = (response.data || []).map(card => ({
                id: card.passcode,
                cid: card.cid,
                tw_name: card.name,
                jp_name: null,
                type: card.type,
                atk: card.atk,
                def: card.def,
                level: card.level,
                race: card.race,
                attribute: card.attribute,
                desc: card.desc,
                image_url: card.image_url
            }));

            // 精確匹配排在前面
            mappedResults.sort((a, b) => {
                const aExact = a.tw_name === query;
                const bExact = b.tw_name === query;
                if (aExact && !bExact) return -1;
                if (!aExact && bExact) return 1;
                return 0;
            });

            setSearchResults(mappedResults);
        } catch (err) {
            console.error('搜尋失敗:', err);
        } finally {
            setSearching(false);
        }
    }, [searchQuery, dbReady]);

    // ============================================================
    // 加入購物車：用 CID 查卡號 → 加入購物車
    // ============================================================
    const handleAddToCart = async (card) => {
        setAddingCards(prev => ({ ...prev, [card.id]: 'loading' }));

        try {
            // 1. 若卡片具備 CID，用 CID 向後端取得卡號列表
            let cardNumbers = [];
            if (card.cid) {
                const cidsRes = await api.get(`/cards/cid/${card.cid}/card-numbers`);
                cardNumbers = cidsRes.data.card_numbers || [];
                console.log(`卡片「${card.tw_name}」爬取到 ${cardNumbers.length} 個卡號:`, cardNumbers.slice(0, 5));
            } else {
                console.warn(`卡片「${card.tw_name}」缺少 CID，無法自動爬取卡號。`);
            }

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

            // 3. 加入新卡片 (包含豐富的卡片資訊)
            cartData.shopping_cart.push({
                card_name_zh: card.tw_name,
                passcode: card.id,
                cid: card.cid,
                type: card.type,
                atk: card.atk,
                def: card.def,
                level: card.level,
                race: card.race,
                attribute: card.attribute,
                image_url: card.image_url,
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
                    passcode: card.id,
                    cid: card.cid,
                    type: card.type,
                    atk: card.atk,
                    def: card.def,
                    level: card.level,
                    race: card.race,
                    attribute: card.attribute,
                    image_url: card.image_url,
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
        return card.image_url || null;
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
