import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { ArrowLeft, Save, Play, Trash2, Plus, Search, Loader2, ShoppingCart } from 'lucide-react';

const ProjectDetail = () => {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const [cart, setCart] = useState({ shopping_cart: [], global_settings: {} });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [running, setRunning] = useState(false);
    const [results, setResults] = useState(null);

    // 取得購物車資料
    useEffect(() => {
        const fetchCart = async () => {
            try {
                const res = await api.get(`/projects/${projectId}/cart`);
                setCart(res.data);
            } catch (error) {
                console.error("取得購物車失敗", error);
            } finally {
                setLoading(false);
            }
        };
        fetchCart();
    }, [projectId]);

    // 儲存購物車
    const handleSave = async () => {
        setSaving(true);
        try {
            await api.post(`/projects/${projectId}/cart`, cart);
            alert('購物車已儲存！');
        } catch (error) {
            alert('儲存失敗，請檢查後端是否正常運作。');
        } finally {
            setSaving(false);
        }
    };

    // 執行爬蟲流程
    const handleRun = async () => {
        setRunning(true);
        try {
            // 先儲存
            await api.post(`/projects/${projectId}/cart`, cart);
            // 執行流程
            await api.post(`/projects/${projectId}/run`);
            // 跳轉至結果頁
            navigate(`/project/${projectId}/results`);
        } catch (error) {
            alert('執行失敗或逾時，請檢查伺服器日誌。');
            setRunning(false);
        }
    };

    // 更新購物車項目
    const updateItem = (index, field, value) => {
        const newCart = [...cart.shopping_cart];
        newCart[index][field] = value;
        setCart({ ...cart, shopping_cart: newCart });
    };

    // 移除購物車項目
    const removeItem = (index) => {
        const newCart = cart.shopping_cart.filter((_, i) => i !== index);
        setCart({ ...cart, shopping_cart: newCart });
    };

    // 手動新增項目
    const addItem = () => {
        setCart({
            ...cart,
            shopping_cart: [
                ...cart.shopping_cart,
                { card_name_zh: "新卡片", target_card_numbers: [], required_amount: 1 }
            ]
        });
    };

    // 新增卡號
    const addCardId = (index, id) => {
        if (!id) return;
        const newCart = [...cart.shopping_cart];
        if (!newCart[index].target_card_numbers.includes(id)) {
            newCart[index].target_card_numbers.push(id.toUpperCase());
        }
        setCart({ ...cart, shopping_cart: newCart });
    };

    // 移除卡號
    const removeCardId = (itemIndex, idIndex) => {
        const newCart = [...cart.shopping_cart];
        newCart[itemIndex].target_card_numbers.splice(idIndex, 1);
        setCart({ ...cart, shopping_cart: newCart });
    };

    if (loading) return <div className="p-8 text-center text-text-muted">正在載入專案...</div>;

    return (
        <div className="space-y-6 max-w-5xl mx-auto">
            {/* 頂部導覽列 */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link to="/" className="p-2 hover:bg-slate-700 rounded-full transition-colors text-text-muted hover:text-white">
                        <ArrowLeft size={24} />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold">{projectId}</h1>
                        <p className="text-text-muted text-sm">共 {cart.shopping_cart.length} 張目標卡片</p>
                    </div>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={handleSave}
                        disabled={saving || running}
                        className="flex items-center gap-2 px-4 py-2 bg-surface border border-slate-600 rounded hover:bg-slate-700 transition-colors"
                    >
                        {saving ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
                        儲存
                    </button>
                    <button
                        onClick={handleRun}
                        disabled={saving || running}
                        className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded font-bold shadow-lg shadow-blue-500/20 transition-all"
                    >
                        {running ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} />}
                        執行爬蟲
                    </button>
                </div>
            </div>

            {/* 主要內容 */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* 左欄：購物車 */}
                <div className="lg:col-span-2 space-y-4">
                    <div className="flex justify-between items-center mb-2">
                        <h2 className="text-xl font-semibold">購物車</h2>
                        <div className="flex gap-2">
                            <button
                                onClick={() => navigate(`/project/${projectId}/search`)}
                                className="text-sm flex items-center gap-1 text-accent hover:underline bg-accent/10 px-3 py-1 rounded"
                            >
                                <Search size={16} /> 搜尋卡片
                            </button>
                            <button onClick={addItem} className="text-sm flex items-center gap-1 text-primary hover:underline bg-primary/10 px-3 py-1 rounded">
                                <Plus size={16} /> 手動新增
                            </button>
                        </div>
                    </div>

                    {cart.shopping_cart.map((item, idx) => {
                        const imgUrl = item.image_url || (item.passcode ? `https://raw.githubusercontent.com/salix5/query-data/gh-pages/pics/${item.passcode}.jpg` : null);

                        // 計算屬性字串
                        let statStr = '';
                        if (item.type && (item.type & 0x1)) { // MONSTER
                            const attrNames = { 1: '地', 2: '水', 4: '炎', 8: '風', 16: '光', 32: '闇', 64: '神' };
                            const raceNames = {
                                0x1: '戰士族', 0x2: '魔法使族', 0x4: '天使族', 0x8: '惡魔族',
                                0x10: '不死族', 0x20: '機械族', 0x40: '水族', 0x80: '炎族',
                                0x100: '岩石族', 0x200: '鳥獸族', 0x400: '植物族', 0x800: '昆蟲族',
                                0x1000: '雷族', 0x2000: '龍族', 0x4000: '獸族', 0x8000: '獸戰士族',
                                0x10000: '恐龍族', 0x20000: '魚族', 0x40000: '海龍族', 0x80000: '爬蟲類族',
                                0x100000: '超能族', 0x200000: '幻神獸族', 0x400000: '創造神族',
                                0x800000: '幻龍族', 0x1000000: '電子界族', 0x2000000: '幻想魔族',
                            };
                            const level = item.level ? item.level & 0xff : '?';
                            statStr = `★${level}`;
                            if (item.attribute) statStr += ` / ${attrNames[item.attribute] || '？'}`;
                            if (item.race) statStr += ` / ${raceNames[item.race] || '？族'}`;
                            // 舊資料可能沒有 atk/def，先不強制顯示
                        }

                        // 判斷是否為編輯模式
                        const isEditing = item.ui_inputVisible;

                        return (
                            <div key={idx} className="bg-surface border border-slate-700 rounded-xl p-4 hover:border-slate-500 transition-all group flex gap-4">
                                {/* 卡圖 */}
                                <div className="w-20 h-28 flex-shrink-0 rounded-lg overflow-hidden bg-slate-800">
                                    {imgUrl ? (
                                        <img
                                            src={imgUrl}
                                            alt={item.card_name_zh}
                                            className="w-full h-full object-cover"
                                            onError={(e) => { e.target.style.display = 'none'; }}
                                        />
                                    ) : (
                                        <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 text-xs text-center p-1">
                                            <div className="text-[10px] break-all">{item.passcode || '無圖'}</div>
                                        </div>
                                    )}
                                </div>

                                {/* 卡片資訊 */}
                                <div className="flex-1 min-w-0 flex flex-col justify-between">
                                    {/* 上半部：標題與操作列 */}
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex-1 min-w-0 pr-4">
                                            {isEditing ? (
                                                <input
                                                    type="text"
                                                    value={item.card_name_zh}
                                                    onChange={(e) => updateItem(idx, 'card_name_zh', e.target.value)}
                                                    className="w-full max-w-xs bg-slate-900 border border-primary/50 text-white px-2 py-1 rounded focus:outline-none focus:border-primary font-bold text-lg mb-1"
                                                    onBlur={() => updateItem(idx, 'ui_inputVisible', false)}
                                                    autoFocus
                                                />
                                            ) : (
                                                <h3
                                                    className="font-bold text-lg text-white truncate cursor-pointer hover:text-primary transition-colors inline-block"
                                                    onClick={() => updateItem(idx, 'ui_inputVisible', true)}
                                                    title="點擊編輯卡名"
                                                >
                                                    {item.card_name_zh}
                                                </h3>
                                            )}

                                            <div className="flex items-center gap-2 mt-1 flex-wrap">
                                                {item.type && (
                                                    <span className={`text-xs px-2 py-0.5 rounded font-medium ${item.type & 0x1 ? 'bg-amber-500/20 text-amber-400' :
                                                        item.type & 0x2 ? 'bg-emerald-500/20 text-emerald-400' :
                                                            item.type & 0x4 ? 'bg-pink-500/20 text-pink-400' :
                                                                'bg-slate-500/20 text-slate-400'
                                                        }`}>
                                                        {item.type & 0x1 ? '怪獸' : item.type & 0x2 ? '魔法' : item.type & 0x4 ? '陷阱' : '卡片'}
                                                    </span>
                                                )}
                                                {statStr && <span className="text-xs text-text-muted">{statStr}</span>}
                                                {item.cid && <span className="text-xs text-text-muted font-mono bg-slate-800 px-1.5 py-0.5 rounded">CID:{item.cid}</span>}
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-3 flex-shrink-0">
                                            <div className="flex items-center bg-slate-900 border border-slate-700 rounded-lg overflow-hidden h-9">
                                                <button
                                                    className="px-3 text-text-muted hover:text-white hover:bg-slate-800 transition-colors h-full"
                                                    onClick={() => updateItem(idx, 'required_amount', Math.max(1, item.required_amount - 1))}
                                                >-</button>
                                                <span className="w-8 text-center font-bold text-sm text-white">{item.required_amount}</span>
                                                <button
                                                    className="px-3 text-text-muted hover:text-white hover:bg-slate-800 transition-colors h-full"
                                                    onClick={() => updateItem(idx, 'required_amount', item.required_amount + 1)}
                                                >+</button>
                                            </div>
                                            <button onClick={() => removeItem(idx)} className="text-slate-500 hover:text-danger p-2 transition-colors rounded hover:bg-danger/10">
                                                <Trash2 size={18} />
                                            </button>
                                        </div>
                                    </div>

                                    {/* 下半部：目標卡號與稀有度標籤 */}
                                    <div className="mt-auto pt-2">
                                        <div className="flex flex-wrap gap-1.5 items-center">
                                            <span className="text-xs text-text-muted font-medium mr-1">目標版本:</span>
                                            {item.target_card_numbers.length === 0 ? (
                                                <span className="text-xs text-danger/80 bg-danger/10 px-2 py-0.5 rounded italic">未指定卡號，爬蟲將跳過此卡</span>
                                            ) : (
                                                item.target_card_numbers.map((cardObj, idIdx) => {
                                                    // 舊資料相容：如果是字串，轉為物件形式
                                                    const isString = typeof cardObj === 'string';
                                                    const displayNum = isString ? cardObj : cardObj.card_number;
                                                    const rarityName = isString ? null : cardObj.rarity_name;

                                                    // 根據稀有度決定標籤顏色
                                                    let bgColor = "bg-slate-700", textColor = "text-slate-200", borderColor = "border-transparent";
                                                    if (rarityName) {
                                                        const r = rarityName.toLowerCase();
                                                        if (r.includes('secret') || r.includes('半鑽') || r.includes('白鑽')) { bgColor = "bg-rose-900/40"; textColor = "text-rose-200"; borderColor = "border-rose-500/30"; }
                                                        else if (r.includes('ultra') || r.includes('金亮')) { bgColor = "bg-amber-900/40"; textColor = "text-amber-200"; borderColor = "border-amber-500/30"; }
                                                        else if (r.includes('super') || r.includes('亮面')) { bgColor = "bg-blue-900/40"; textColor = "text-blue-200"; borderColor = "border-blue-500/30"; }
                                                        else if (r.includes('normal') || r.includes('普卡')) { bgColor = "bg-slate-800"; textColor = "text-slate-300"; borderColor = "border-slate-600"; }
                                                        else { bgColor = "bg-purple-900/40"; textColor = "text-purple-200"; borderColor = "border-purple-500/30"; }
                                                    }

                                                    return (
                                                        <div key={idIdx} className={`group/tag flex items-center text-xs px-2 py-1 rounded border ${bgColor} ${textColor} ${borderColor} transition-colors cursor-default`} title={isString ? '指定卡號' : `${cardObj.pack_name} - ${rarityName}`}>
                                                            <span className="font-mono">{displayNum}</span>
                                                            {rarityName && <span className="ml-1 opacity-75 hidden sm:inline-block">({rarityName})</span>}
                                                            <button
                                                                onClick={(e) => { e.stopPropagation(); removeCardId(idx, idIdx); }}
                                                                className="ml-1.5 -mr-0.5 opacity-50 hover:opacity-100 hover:text-danger focus:outline-none transition-opacity"
                                                            >×</button>
                                                        </div>
                                                    );
                                                })
                                            )}

                                            {/* 手動新增卡號 輸入框 */}
                                            <div className="relative flex items-center">
                                                {item.ui_inputVisible ? (
                                                    <input
                                                        type="text"
                                                        placeholder="輸入卡號..."
                                                        className="bg-slate-900 border border-primary/50 text-white text-xs px-2 py-1 rounded w-24 focus:outline-none focus:border-primary"
                                                        onBlur={() => updateItem(idx, 'ui_inputVisible', false)}
                                                        onKeyDown={(e) => {
                                                            if (e.key === 'Enter' && e.target.value.trim()) {
                                                                addCardId(idx, e.target.value.trim());
                                                                e.target.value = '';
                                                            } else if (e.key === 'Escape') {
                                                                updateItem(idx, 'ui_inputVisible', false);
                                                            }
                                                        }}
                                                        autoFocus
                                                    />
                                                ) : (
                                                    <button
                                                        onClick={() => updateItem(idx, 'ui_inputVisible', true)}
                                                        className="text-xs text-primary/70 hover:text-primary hover:bg-primary/10 px-2 py-1 rounded transition-colors flex items-center gap-1 border border-dashed border-primary/30"
                                                    >
                                                        <Plus size={12} /> 手動增刪
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}

                    {cart.shopping_cart.length === 0 && (
                        <div className="p-12 text-center border border-dashed border-slate-700 bg-surface/50 rounded-xl text-text-muted flex flex-col items-center">
                            <ShoppingCart size={48} className="opacity-20 mb-4 text-primary" />
                            <h3 className="text-lg font-medium text-white mb-2">購物車是空的</h3>
                            <p className="text-sm max-w-sm mb-6">點擊上方「搜尋卡片」來尋找想要的卡片，系統會自動帶入卡號與稀有度。</p>
                            <button
                                onClick={() => navigate(`/project/${projectId}/search`)}
                                className="bg-primary hover:bg-primary-hover text-white px-6 py-2 rounded-lg font-medium transition-colors"
                            >
                                前往搜尋卡片
                            </button>
                        </div>
                    )}
                </div>

                {/* 右欄：設定與結果 */}
                <div className="space-y-6">

                    {/* 全域設定面板 */}
                    <div className="bg-surface border border-slate-700 rounded-lg p-5">
                        <h3 className="text-sm font-bold text-text-muted uppercase tracking-wider mb-4">全域設定</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="text-sm block mb-1">預設運費</label>
                                <input
                                    type="number"
                                    value={cart.global_settings.default_shipping_cost || 60}
                                    onChange={(e) => setCart({ ...cart, global_settings: { ...cart.global_settings, default_shipping_cost: parseInt(e.target.value) } })}
                                    className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm"
                                />
                            </div>
                            <div>
                                <label className="text-sm block mb-1">最低消費門檻</label>
                                <input
                                    type="number"
                                    value={cart.global_settings.min_purchase_limit || 100}
                                    onChange={(e) => setCart({ ...cart, global_settings: { ...cart.global_settings, min_purchase_limit: parseInt(e.target.value) } })}
                                    className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProjectDetail;
