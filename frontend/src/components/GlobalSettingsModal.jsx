import React, { useState, useEffect } from 'react';
import { Settings, Save, RotateCcw, Plus, X } from 'lucide-react';
import api from '../lib/api';
import ApiErrorBanner from './ApiErrorBanner';

/**
 * GlobalSettingsModal - 全域設定 Modal
 * ======================================
 * 從右上角齒輪按鈕開啟，管理 4 項全域設定：
 * 1. 預設運費 (default_shipping_cost)
 * 2. 每家最低消費 (min_purchase_limit)
 * 3. 排除關鍵字 (global_exclude_keywords)
 * 4. 封鎖賣家 ID (global_exclude_seller)
 *
 * v0.3.0: 從側邊欄嵌入改為獨立 Modal，解決空間不足的問題。
 */
const GlobalSettingsModal = ({ isOpen, onClose }) => {
    const [settings, setSettings] = useState({
        default_shipping_cost: 60,
        min_purchase_limit: 0,
        global_exclude_keywords: [],
        global_exclude_seller: [],
    });

    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);
    const [saveSuccess, setSaveSuccess] = useState(false);

    // Tag 輸入暫存
    const [keywordInput, setKeywordInput] = useState('');
    const [sellerInput, setSellerInput] = useState('');

    // 數字輸入用字串狀態（修正「刪不掉開頭 0」的 bug）
    const [shippingStr, setShippingStr] = useState('60');
    const [minPurchaseStr, setMinPurchaseStr] = useState('0');

    // ============================================================
    // Modal 開啟時載入設定
    // ============================================================
    useEffect(() => {
        if (isOpen) loadSettings();
    }, [isOpen]);

    // ESC 關閉
    useEffect(() => {
        if (!isOpen) return;
        const handleEsc = (e) => { if (e.key === 'Escape') onClose(); };
        document.addEventListener('keydown', handleEsc);
        return () => document.removeEventListener('keydown', handleEsc);
    }, [isOpen, onClose]);

    // 防止背景捲動
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
            return () => { document.body.style.overflow = ''; };
        }
    }, [isOpen]);

    // ============================================================
    // API
    // ============================================================
    const loadSettings = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await api.get('/settings');
            setSettings(res.data);
            setShippingStr(String(res.data.default_shipping_cost));
            setMinPurchaseStr(String(res.data.min_purchase_limit));
        } catch (err) {
            setError(err);
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        // 先把字串同步回 settings
        const finalSettings = {
            ...settings,
            default_shipping_cost: parseInt(shippingStr) || 0,
            min_purchase_limit: parseInt(minPurchaseStr) || 0,
        };
        setSaving(true);
        setError(null);
        setSaveSuccess(false);
        try {
            await api.put('/settings', finalSettings);
            setSettings(finalSettings);
            setSaveSuccess(true);
            setTimeout(() => setSaveSuccess(false), 3000);
        } catch (err) {
            setError(err);
        } finally {
            setSaving(false);
        }
    };

    const handleReset = () => {
        setSettings({
            default_shipping_cost: 60,
            min_purchase_limit: 0,
            global_exclude_keywords: [],
            global_exclude_seller: [],
        });
        setShippingStr('60');
        setMinPurchaseStr('0');
    };

    // ============================================================
    // Tag 管理（修正 Bug 3：重複時也清空輸入框）
    // ============================================================
    const addTag = (field, value, setInputFn) => {
        const trimmed = value.trim();
        if (!trimmed) return;
        if (settings[field].includes(trimmed)) {
            setInputFn(''); // 重複也清空，不然使用者要手動刪
            return;
        }
        setSettings(prev => ({
            ...prev,
            [field]: [...prev[field], trimmed],
        }));
        setInputFn('');
    };

    const removeTag = (field, index) => {
        setSettings(prev => ({
            ...prev,
            [field]: prev[field].filter((_, i) => i !== index),
        }));
    };

    const handleKeyDown = (e, field, value, setInputFn) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addTag(field, value, setInputFn);
        }
    };

    // ============================================================
    // 數字 Stepper 共用元件
    // ============================================================
    const NumericStepper = ({ strValue, setStrValue, onUpdate, step = 10, min = 0 }) => (
        <div className="flex items-center bg-slate-900 border border-slate-700 rounded-lg overflow-hidden h-10">
            <button
                className="px-4 text-text-muted hover:text-white hover:bg-slate-800 transition-colors h-full text-lg font-bold"
                onClick={() => {
                    const v = Math.max(min, (parseInt(strValue) || 0) - step);
                    setStrValue(String(v));
                    onUpdate(v);
                }}
            >−</button>
            <input
                type="text"
                inputMode="numeric"
                value={strValue}
                onChange={(e) => {
                    if (e.target.value === '' || /^\d+$/.test(e.target.value)) {
                        setStrValue(e.target.value);
                    }
                }}
                onBlur={() => {
                    const n = parseInt(strValue) || 0;
                    setStrValue(String(n));
                    onUpdate(n);
                }}
                className="flex-1 text-center font-bold text-white bg-transparent outline-none text-sm"
            />
            <button
                className="px-4 text-text-muted hover:text-white hover:bg-slate-800 transition-colors h-full text-lg font-bold"
                onClick={() => {
                    const v = (parseInt(strValue) || 0) + step;
                    setStrValue(String(v));
                    onUpdate(v);
                }}
            >+</button>
        </div>
    );

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center animate-modalFadeIn"
            onClick={onClose}
        >
            {/* 背景遮罩 */}
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

            {/* Modal 本體 */}
            <div
                className="relative bg-surface border border-slate-600 rounded-2xl shadow-2xl w-full max-w-lg mx-4 animate-modalSlideIn max-h-[85vh] flex flex-col"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-5 border-b border-slate-700 flex-shrink-0">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2.5">
                        <div className="p-2 bg-primary/20 rounded-lg">
                            <Settings size={20} className="text-primary" />
                        </div>
                        全域設定
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-slate-700 rounded-lg transition-colors text-text-muted hover:text-white"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Body */}
                <div className="px-6 py-5 space-y-5 overflow-y-auto flex-1">
                    {error && <ApiErrorBanner error={error} />}

                    {loading ? (
                        <div className="text-center text-text-muted py-8">
                            <div className="animate-pulse text-lg">載入設定中...</div>
                        </div>
                    ) : (
                        <>
                            {/* 預設運費 */}
                            <div>
                                <label className="block text-sm font-medium text-text-muted mb-2">
                                    🚚 預設運費（元）
                                </label>
                                <NumericStepper
                                    strValue={shippingStr}
                                    setStrValue={setShippingStr}
                                    onUpdate={(v) => setSettings(p => ({ ...p, default_shipping_cost: v }))}
                                />
                            </div>

                            {/* 每家最低消費 */}
                            <div>
                                <label className="block text-sm font-medium text-text-muted mb-2">
                                    💰 每家最低消費（0 = 不限）
                                </label>
                                <NumericStepper
                                    strValue={minPurchaseStr}
                                    setStrValue={setMinPurchaseStr}
                                    onUpdate={(v) => setSettings(p => ({ ...p, min_purchase_limit: v }))}
                                />
                            </div>

                            {/* 排除關鍵字 */}
                            <div>
                                <label className="block text-sm font-medium text-text-muted mb-2">
                                    🚫 排除關鍵字
                                </label>
                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        value={keywordInput}
                                        onChange={(e) => setKeywordInput(e.target.value)}
                                        onKeyDown={(e) => handleKeyDown(e, 'global_exclude_keywords', keywordInput, setKeywordInput)}
                                        placeholder="例如：卡套"
                                        className="flex-1 px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-sm text-text
                                                placeholder:text-slate-500 focus:outline-none focus:border-primary
                                                focus:ring-1 focus:ring-primary/50 transition-colors"
                                    />
                                    <button
                                        onClick={() => addTag('global_exclude_keywords', keywordInput, setKeywordInput)}
                                        className="px-3 py-2.5 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors"
                                        title="新增"
                                    >
                                        <Plus size={16} />
                                    </button>
                                </div>
                                <div className="flex flex-wrap gap-2 mt-2.5">
                                    {settings.global_exclude_keywords.map((kw, i) => (
                                        <span
                                            key={i}
                                            className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-danger/20 text-danger
                                                    text-xs rounded-full border border-danger/30 font-medium"
                                        >
                                            {kw}
                                            <button
                                                onClick={() => removeTag('global_exclude_keywords', i)}
                                                className="hover:text-white transition-colors"
                                            >
                                                <X size={12} />
                                            </button>
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* 封鎖賣家 ID */}
                            <div>
                                <label className="block text-sm font-medium text-text-muted mb-2">
                                    🛑 封鎖賣家 ID
                                </label>
                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        value={sellerInput}
                                        onChange={(e) => setSellerInput(e.target.value)}
                                        onKeyDown={(e) => handleKeyDown(e, 'global_exclude_seller', sellerInput, setSellerInput)}
                                        placeholder="輸入賣家 ID"
                                        className="flex-1 px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-sm text-text
                                                placeholder:text-slate-500 focus:outline-none focus:border-primary
                                                focus:ring-1 focus:ring-primary/50 transition-colors font-mono"
                                    />
                                    <button
                                        onClick={() => addTag('global_exclude_seller', sellerInput, setSellerInput)}
                                        className="px-3 py-2.5 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors"
                                        title="新增"
                                    >
                                        <Plus size={16} />
                                    </button>
                                </div>
                                <div className="flex flex-wrap gap-2 mt-2.5">
                                    {settings.global_exclude_seller.map((id, i) => (
                                        <span
                                            key={i}
                                            className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-amber-500/20 text-amber-400
                                                    text-xs rounded-full border border-amber-500/30 font-mono font-medium"
                                        >
                                            {id}
                                            <button
                                                onClick={() => removeTag('global_exclude_seller', i)}
                                                className="hover:text-white transition-colors"
                                            >
                                                <X size={12} />
                                            </button>
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </>
                    )}
                </div>

                {/* Footer */}
                {!loading && (
                    <div className="px-6 py-4 border-t border-slate-700 flex-shrink-0">
                        <div className="flex gap-3">
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5
                                        bg-primary text-white font-medium rounded-lg
                                        hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed
                                        transition-colors"
                            >
                                <Save size={16} />
                                {saving ? '儲存中...' : '儲存設定'}
                            </button>
                            <button
                                onClick={handleReset}
                                className="flex items-center justify-center gap-2 px-4 py-2.5
                                        bg-slate-700 text-text-muted rounded-lg
                                        hover:bg-slate-600 hover:text-white transition-colors"
                                title="重置為預設值"
                            >
                                <RotateCcw size={16} />
                            </button>
                        </div>
                        {saveSuccess && (
                            <div className="text-center text-success text-sm py-2 animate-fadeIn mt-2">
                                ✅ 設定已儲存
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default GlobalSettingsModal;
