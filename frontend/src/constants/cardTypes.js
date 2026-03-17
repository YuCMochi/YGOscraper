/**
 * src/constants/cardTypes.js - 遊戲王卡片類型常數與名稱對應
 * ============================================================
 * 統一管理所有卡片類型旗標、種族名稱、屬性名稱的定義。
 * CardSearchPage 和 ProjectDetail 都共用這裡的常數與 helper 函數。
 * 
 * 資料來源：YGOPro cards.cdb 的位元旗標定義
 * （參考 https://github.com/Fluorohydride/ygopro）
 */

// ============================================================
// 卡片類型旗標（Bitflag）
// ============================================================
export const TYPE_MONSTER    = 0x1;
export const TYPE_SPELL      = 0x2;
export const TYPE_TRAP       = 0x4;
export const TYPE_NORMAL     = 0x10;
export const TYPE_EFFECT     = 0x20;
export const TYPE_FUSION     = 0x40;
export const TYPE_RITUAL     = 0x80;
export const TYPE_SPIRIT     = 0x200;
export const TYPE_UNION      = 0x400;
export const TYPE_DUAL       = 0x800;
export const TYPE_TUNER      = 0x1000;
export const TYPE_SYNCHRO    = 0x2000;
export const TYPE_TOKEN      = 0x4000;
export const TYPE_QUICKPLAY  = 0x10000;
export const TYPE_CONTINUOUS = 0x20000;
export const TYPE_EQUIP      = 0x40000;
export const TYPE_FIELD      = 0x80000;
export const TYPE_COUNTER    = 0x100000;
export const TYPE_FLIP       = 0x200000;
export const TYPE_TOON       = 0x400000;
export const TYPE_XYZ        = 0x800000;
export const TYPE_PENDULUM   = 0x1000000;
export const TYPE_SPSUMMON   = 0x2000000;
export const TYPE_LINK       = 0x4000000;

// ============================================================
// 卡片類型名稱對應（繁體中文）
// ============================================================
export const typeNames = {
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

// ============================================================
// 屬性名稱對應
// ============================================================
export const attrNames = {
    1: '地', 2: '水', 4: '炎', 8: '風', 16: '光', 32: '闇', 64: '神',
};

// ============================================================
// 種族名稱對應
// ============================================================
export const raceNames = {
    0x1: '戰士族', 0x2: '魔法使族', 0x4: '天使族', 0x8: '惡魔族',
    0x10: '不死族', 0x20: '機械族', 0x40: '水族', 0x80: '炎族',
    0x100: '岩石族', 0x200: '鳥獸族', 0x400: '植物族', 0x800: '昆蟲族',
    0x1000: '雷族', 0x2000: '龍族', 0x4000: '獸族', 0x8000: '獸戰士族',
    0x10000: '恐龍族', 0x20000: '魚族', 0x40000: '海龍族', 0x80000: '爬蟲類族',
    0x100000: '超能族', 0x200000: '幻神獸族', 0x400000: '創造神族',
    0x800000: '幻龍族', 0x1000000: '電子界族', 0x2000000: '幻想魔族',
};

// ============================================================
// 特殊 ID 常數
// ============================================================
export const ID_TYLER = 68811206;
export const ID_DECOY = 20240828;
export const ARTWORK_OFFSET = 20;
export const MAX_CARD_ID = 99999999;

// ============================================================
// 輔助函數（Helper Functions）
// ============================================================

/** 取得卡片的類型描述字串（例如：「怪獸/同步/效果/協調」）*/
export function getTypeString(type) {
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

/** 顯示攻擊力/守備力數值（-2 代表 '?'）*/
export function printAD(x) {
    return x === -2 ? '?' : String(x);
}

/** 取得卡片的統計資訊字串（例如：「★4 / 光 / 戰士族 / 攻1500 / 守1200」）*/
export function getStatString(card) {
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
