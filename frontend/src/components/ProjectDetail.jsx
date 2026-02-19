import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { ArrowLeft, Save, Play, Trash2, Plus, Search, Loader2 } from 'lucide-react';

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
            alert('流程已完成！請查看結果。');
            // 取得結果
            const res = await api.get(`/projects/${projectId}/results`);
            setResults(res.data);
        } catch (error) {
            alert('執行失敗或逾時，請檢查伺服器日誌。');
        } finally {
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

                    {cart.shopping_cart.map((item, idx) => (
                        <div key={idx} className="bg-surface border border-slate-700 rounded-lg p-5 hover:border-slate-500 transition-colors group">
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex-1 mr-4">
                                    <label className="text-xs text-text-muted uppercase font-bold tracking-wider mb-1 block">卡片名稱</label>
                                    <input
                                        type="text"
                                        value={item.card_name_zh}
                                        onChange={(e) => updateItem(idx, 'card_name_zh', e.target.value)}
                                        className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 focus:outline-none focus:border-primary transition-colors font-medium text-lg"
                                    />
                                </div>
                                <button onClick={() => removeItem(idx)} className="text-slate-600 hover:text-danger p-2 transition-colors">
                                    <Trash2 size={20} />
                                </button>
                            </div>

                            <div className="flex gap-4">
                                <div className="w-24">
                                    <label className="text-xs text-text-muted uppercase font-bold tracking-wider mb-1 block">數量</label>
                                    <input
                                        type="number"
                                        min="1"
                                        value={item.required_amount}
                                        onChange={(e) => updateItem(idx, 'required_amount', parseInt(e.target.value))}
                                        className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 focus:outline-none focus:border-primary text-center"
                                    />
                                </div>
                                <div className="flex-1">
                                    <label className="text-xs text-text-muted uppercase font-bold tracking-wider mb-1 block">目標卡號（按 Enter 新增）</label>
                                    <div className="flex flex-wrap gap-2 items-center bg-slate-900 border border-slate-700 rounded px-3 py-2 min-h-[42px]">
                                        {item.target_card_numbers.map((id, idIdx) => (
                                            <span key={idIdx} className="bg-slate-700 text-xs px-2 py-1 rounded flex items-center gap-1">
                                                {id}
                                                <button onClick={() => removeCardId(idx, idIdx)} className="hover:text-danger">×</button>
                                            </span>
                                        ))}
                                        <input
                                            type="text"
                                            placeholder="例如 DABL-JP001"
                                            className="bg-transparent focus:outline-none min-w-[100px] text-sm"
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter') {
                                                    addCardId(idx, e.target.value);
                                                    e.target.value = '';
                                                }
                                            }}
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}

                    {cart.shopping_cart.length === 0 && (
                        <div className="p-8 text-center border-2 border-dashed border-slate-700 rounded-lg text-text-muted">
                            購物車是空的。點擊「搜尋卡片」或「手動新增」來新增卡片。
                        </div>
                    )}
                </div>

                {/* 右欄：設定與結果 */}
                <div className="space-y-6">
                    {/* 結果面板 */}
                    {results && (
                        <div className="bg-slate-900/50 border border-green-500/30 rounded-lg p-5">
                            <h3 className="text-lg font-bold text-green-400 mb-4 flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                                最佳化結果
                            </h3>
                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-text-muted">總花費：</span>
                                    <span className="font-bold text-lg text-white">${results.summary.grand_total}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-text-muted">運費：</span>
                                    <span>${results.summary.total_shipping_cost}</span>
                                </div>
                                <div className="h-px bg-slate-700 my-2"></div>
                                <div className="space-y-2">
                                    <div className="font-medium text-text-muted mb-1">購買店家：</div>
                                    {Object.keys(results.sellers).map(seller => (
                                        <div key={seller} className="flex justify-between text-xs bg-slate-800 p-2 rounded">
                                            <span className="truncate max-w-[150px]">{seller}</span>
                                            <span className="text-primary">${results.sellers[seller].items_subtotal}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

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
