import React, { useState, useEffect } from 'react';
import { Save, RotateCcw, Plus, X, ChevronDown, ChevronUp } from 'lucide-react';
import api from '../lib/api';
import ApiErrorBanner from './ApiErrorBanner';

/**
 * GlobalSettingsPanel - 全域設定面板
 * ====================================
 * 嵌入側邊欄中，讓使用者管理 4 項全域設定：
 * 1. 預設運費 (default_shipping_cost)
 * 2. 每家最低消費 (min_purchase_limit)
 * 3. 排除關鍵字 (global_exclude_keywords)
 * 4. 封鎖賣家 ID (global_exclude_seller)
 *
 * 修改後需按「儲存」才會寫入 data/global_settings.json。
 */
const GlobalSettingsPanel = ({ isOpen, onToggle }) => {
    // 設定狀態
    const [settings, setSettings] = useState({
        default_shipping_cost: 60,
        min_purchase_limit: 0,
        global_exclude_keywords: [],
        global_exclude_seller: [],
    });

    // UI 狀態
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);
    const [saveSuccess, setSaveSuccess] = useState(false);

    // Tag 輸入暫存
    const [keywordInput, setKeywordInput] = useState('');
    const [sellerInput, setSellerInput] = useState('');

    // ============================================================
    // 讀取全域設定
    // ============================================================
    useEffect(() => {
        if (isOpen) {
            loadSettings();
        }
    }, [isOpen]);

    const loadSettings = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await api.get('/settings');
            setSettings(res.data);
        } catch (err) {
            setError(err);
        } finally {
            setLoading(false);
        }
    };

    // ============================================================
    // 儲存全域設定
    // ============================================================
    const handleSave = async () => {
        setSaving(true);
        setError(null);
        setSaveSuccess(false);
        try {
            await api.put('/settings', settings);
            setSaveSuccess(true);
            // 3 秒後清除成功提示
            setTimeout(() => setSaveSuccess(false), 3000);
        } catch (err) {
            setError(err);
        } finally {
            setSaving(false);
        }
    };

    // ============================================================
    // 重置為預設值
    // ============================================================
    const handleReset = () => {
        setSettings({
            default_shipping_cost: 60,
            min_purchase_limit: 0,
            global_exclude_keywords: [],
            global_exclude_seller: [],
        });
    };

    // ============================================================
    // Tag 管理（關鍵字 & 賣家 ID）
    // ============================================================
    const addTag = (field, value, setInputFn) => {
        const trimmed = value.trim();
        if (!trimmed) return;
        if (settings[field].includes(trimmed)) return; // 不重複
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

    // 面板收合時不渲染內容
    if (!isOpen) return null;

    return (
        <div className="px-4 py-3 border-t border-slate-700 space-y-4 animate-fadeIn">
            {/* 錯誤提示 */}
            {error && <ApiErrorBanner error={error} />}

            {loading ? (
                <div className="text-center text-text-muted py-4">
                    <div className="animate-pulse">載入設定中...</div>
                </div>
            ) : (
                <>
                    {/* 預設運費 */}
                    <div>
                        <label className="block text-xs text-text-muted mb-1">
                            🚚 預設運費（元）
                        </label>
                        <input
                            type="number"
                            min="0"
                            max="200"
                            value={settings.default_shipping_cost}
                            onChange={(e) => setSettings(prev => ({
                                ...prev,
                                default_shipping_cost: parseInt(e.target.value) || 0,
                            }))}
                            className="w-full px-3 py-2 bg-background border border-slate-600 rounded-lg text-sm text-text
                                    focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50
                                    transition-colors"
                        />
                    </div>

                    {/* 每家最低消費 */}
                    <div>
                        <label className="block text-xs text-text-muted mb-1">
                            💰 每家最低消費（0 = 不限）
                        </label>
                        <input
                            type="number"
                            min="0"
                            value={settings.min_purchase_limit}
                            onChange={(e) => setSettings(prev => ({
                                ...prev,
                                min_purchase_limit: parseInt(e.target.value) || 0,
                            }))}
                            className="w-full px-3 py-2 bg-background border border-slate-600 rounded-lg text-sm text-text
                                    focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50
                                    transition-colors"
                        />
                    </div>

                    {/* 排除關鍵字 */}
                    <div>
                        <label className="block text-xs text-text-muted mb-1">
                            🚫 排除關鍵字
                        </label>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={keywordInput}
                                onChange={(e) => setKeywordInput(e.target.value)}
                                onKeyDown={(e) => handleKeyDown(e, 'global_exclude_keywords', keywordInput, setKeywordInput)}
                                placeholder="例如：卡套"
                                className="flex-1 px-3 py-2 bg-background border border-slate-600 rounded-lg text-sm text-text
                                        placeholder:text-slate-500 focus:outline-none focus:border-primary
                                        focus:ring-1 focus:ring-primary/50 transition-colors"
                            />
                            <button
                                onClick={() => addTag('global_exclude_keywords', keywordInput, setKeywordInput)}
                                className="px-2 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30
                                        transition-colors"
                                title="新增"
                            >
                                <Plus size={16} />
                            </button>
                        </div>
                        {/* Tag 清單 */}
                        <div className="flex flex-wrap gap-1.5 mt-2">
                            {settings.global_exclude_keywords.map((kw, i) => (
                                <span
                                    key={i}
                                    className="inline-flex items-center gap-1 px-2 py-0.5 bg-danger/20 text-danger
                                            text-xs rounded-full border border-danger/30"
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
                        <label className="block text-xs text-text-muted mb-1">
                            🛑 封鎖賣家 ID
                        </label>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={sellerInput}
                                onChange={(e) => setSellerInput(e.target.value)}
                                onKeyDown={(e) => handleKeyDown(e, 'global_exclude_seller', sellerInput, setSellerInput)}
                                placeholder="輸入賣家 ID"
                                className="flex-1 px-3 py-2 bg-background border border-slate-600 rounded-lg text-sm text-text
                                        placeholder:text-slate-500 focus:outline-none focus:border-primary
                                        focus:ring-1 focus:ring-primary/50 transition-colors"
                            />
                            <button
                                onClick={() => addTag('global_exclude_seller', sellerInput, setSellerInput)}
                                className="px-2 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30
                                        transition-colors"
                                title="新增"
                            >
                                <Plus size={16} />
                            </button>
                        </div>
                        {/* Tag 清單 */}
                        <div className="flex flex-wrap gap-1.5 mt-2">
                            {settings.global_exclude_seller.map((id, i) => (
                                <span
                                    key={i}
                                    className="inline-flex items-center gap-1 px-2 py-0.5 bg-amber-500/20 text-amber-400
                                            text-xs rounded-full border border-amber-500/30 font-mono"
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

                    {/* 操作按鈕列 */}
                    <div className="flex gap-2 pt-2">
                        <button
                            onClick={handleSave}
                            disabled={saving}
                            className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2
                                    bg-primary text-white text-sm font-medium rounded-lg
                                    hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed
                                    transition-colors"
                        >
                            <Save size={14} />
                            {saving ? '儲存中...' : '儲存'}
                        </button>
                        <button
                            onClick={handleReset}
                            className="flex items-center justify-center gap-1.5 px-3 py-2
                                    bg-slate-700 text-text-muted text-sm rounded-lg
                                    hover:bg-slate-600 hover:text-white transition-colors"
                            title="重置為預設值"
                        >
                            <RotateCcw size={14} />
                        </button>
                    </div>

                    {/* 儲存成功提示 */}
                    {saveSuccess && (
                        <div className="text-center text-success text-xs py-1 animate-fadeIn">
                            ✅ 設定已儲存
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default GlobalSettingsPanel;
