/**
 * src/constants/rarityTypes.js - 稀有度 ID 對照表與顏色樣式
 * ============================================================
 * 資料來源：Konami 官方卡片資料庫 CSS class (rid_XX)
 * 對應關係由爬蟲腳本從 Konami DB 提取（2026-03-28）
 *
 * 每張卡的 target_card_numbers 中會帶 rarity_id（字串），
 * 前端用此表查找對應的簡稱、全名、中文通稱和顏色。
 */

// ============================================================
// Rarity ID → 稀有度資訊對照表
// ============================================================
export const RARITY_MAP = {
    '1':  { short: 'N',       full: 'ノーマル',                                              zh: '普卡',       color: '#9c9c9c' },
    '2':  { short: 'R',       full: 'レア',                                                  zh: '銀字',       color: '#81c67f' },
    '3':  { short: 'SR',      full: 'スーパーレア',                                            zh: '亮面',       color: '#6aa1cf' },
    '4':  { short: 'UR',      full: 'ウルトラレア',                                            zh: '金亮',       color: '#cfa15e' },
    '5':  { short: 'SE',      full: 'シークレットレア',                                         zh: '半鑽',       color: '#e86d6d' },
    '6':  { short: 'UL',      full: 'アルティメットレア',                                       zh: '浮雕',       color: '#d87ce6' },
    '7':  { short: 'HR',      full: 'ホログラフィックレア',                                     zh: '雷射',       color: '#779aad' },
    '8':  { short: 'GR',      full: 'ゴールドレア',                                            zh: '黃金',       color: '#adae29' },
    '9':  { short: 'P',       full: 'パラレル',                                                zh: '普鑽',       color: '#957fd5' },
    '11': { short: 'P+UR',    full: 'パラレルウルトラレア',                                     zh: '鑽面金亮',   color: '#957fd5' },
    '12': { short: 'P+SR',    full: 'パラレルスーパーレア',                                     zh: '鑽面亮面',   color: '#957fd5' },
    '15': { short: 'EXSE',    full: 'エクストラシークレットレア',                                zh: '全鑽',       color: '#e86d6d' },
    '16': { short: 'CR',      full: 'コレクターズレア',                                         zh: '雕鑽',       color: '#d8b13e' },
    '21': { short: 'KC',      full: 'KC',                                                    zh: 'KC普卡',     color: '#346ecc' },
    '24': { short: 'KC+UR',   full: 'KCウルトラレア',                                          zh: 'KC金亮',     color: '#346ecc' },
    '26': { short: 'M',       full: 'ミレニアム',                                              zh: '古文鑽',     color: '#ce720e' },
    '29': { short: 'M+UR',    full: 'ミレニアムウルトラレア',                                   zh: '金亮古文鑽', color: '#ce720e' },
    '33': { short: 'P+HR',    full: 'パラレルホログラフィックレア',                              zh: '鑽面雷射',   color: '#957fd5' },
    '35': { short: '20th SE', full: '20thシークレットレア',                                     zh: '20th紅鑽',   color: '#e86d6d' },
    '36': { short: 'PSE',     full: 'プリズマティックシークレットレア',                           zh: '白鑽',       color: '#e86d6d' },
    '38': { short: 'PG',      full: 'プレミアムゴールドレア',                                   zh: '高級黄金',   color: '#adae29' },
    '43': { short: 'SE',      full: 'シークレットレア（SPECIAL BLUE Ver.）',                    zh: '藍鑽',       color: '#e86d6d' },
    '51': { short: 'QCSE',    full: 'クォーターセンチュリーシークレットレア',                     zh: '25th金鑽',   color: '#e86d6d' },
    '53': { short: 'QCSE',    full: 'クォーターセンチュリーシークレットレア（TOKYO DOME GREEN Ver.）', zh: '25th綠鑽', color: '#e86d6d' },
};

// ============================================================
// 未知稀有度的預設值
// ============================================================
const UNKNOWN_RARITY = {
    short: '?',
    full: '不明',
    zh: '不明',
    color: '#64748b', // slate-500
};

// ============================================================
// Helper Functions
// ============================================================

/**
 * 根據 rid 取得稀有度資訊物件
 * @param {string|number} rid - Rarity ID
 * @returns {{ short: string, full: string, zh: string, color: string }}
 */
export function getRarityInfo(rid) {
    if (!rid) return UNKNOWN_RARITY;
    return RARITY_MAP[String(rid)] || UNKNOWN_RARITY;
}

/**
 * 根據 rid 取得暗色主題的 inline style
 *
 * 設計原則：
 * - 文字色 = CSV 的 color（已適合暗色背景上閱讀）
 * - 邊框色 = color + 50% 透明度
 * - 背景色 = color + 15% 透明度（微微帶色的暗底）
 *
 * @param {string|number} rid - Rarity ID
 * @returns {{ backgroundColor: string, color: string, borderColor: string }}
 */
export function getRarityStyle(rid) {
    const info = getRarityInfo(rid);
    const hex = info.color;

    // 將 hex 轉為 rgb 值
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);

    return {
        backgroundColor: `rgba(${r}, ${g}, ${b}, 0.15)`,
        color: hex,
        borderColor: `rgba(${r}, ${g}, ${b}, 0.4)`,
    };
}

/**
 * 取得 hover tooltip 用的顯示文字
 * 格式：「ウルトラレア（金亮）」
 *
 * @param {string|number} rid - Rarity ID
 * @returns {string}
 */
export function getRarityDisplay(rid) {
    const info = getRarityInfo(rid);
    if (info === UNKNOWN_RARITY) return '不明稀有度';
    return `${info.full}（${info.zh}）`;
}
