import React, { useState, useMemo, useEffect, useRef } from 'react';
import { 
  ShoppingCart, 
  Settings, 
  Copy, 
  Download, 
  Trash2, 
  Plus, 
  FileJson,
  RotateCcw,
  X,
  Languages,
  Minus,
  AlertCircle,
  CheckCircle2,
  FileEdit
} from 'lucide-react';
import TagInput from './components/TagInput';
import { GlobalSettings, CartItemInternal, OutputJson } from './types';

const PRESET_KEYWORDS = ["卡套", "桌墊", "福袋", "影印", "亞英", "美英", "簡中", "只有書", "損卡"];

// Translation Dictionary
const TRANSLATIONS = {
  zh: {
    appTitle: "設定檔產生器",
    resetDefaults: "重置預設值",
    globalSettings: "全域設定",
    defaultShipping: "預設運費",
    excludeKeywords: "排除關鍵字",
    addKeywordPlaceholder: "新增自訂關鍵字...",
    add: "新增",
    excludeSellers: "賣家黑名單",
    excludeSellersHelper: "按 Enter 新增賣家代號",
    shoppingCart: "購物車",
    cardLabel: "卡片",
    cardName: "卡片名稱 (中文)",
    cardNamePlaceholder: "例如：原始生命態 尼比魯",
    quantity: "數量",
    targetIds: "卡片編號",
    targetIdsPlaceholder: "例如：QCAC-JP010",
    targetIdsHelper: "新增可接受的卡號版本 (按 Enter 新增)",
    addCard: "新增卡片",
    jsonOutput: "JSON 輸出 (可編輯)",
    copy: "複製",
    copied: "已複製！",
    download: "下載 JSON",
    tipTitle: "提示：",
    tipContent: "請務必核對「卡片編號」與官方資料庫是否相符。本工具僅協助產生格式，搜尋準確性取決於您的輸入。",
    tagInputDefaultPlaceholder: "輸入文字並按 Enter...",
    jsonError: "JSON 格式錯誤",
    jsonValid: "格式正確",
    jsonEditHint: "您可直接在此貼上或編輯 JSON，左側介面將自動同步。",
    fileNamePlaceholder: "檔案名稱"
  },
  en: {
    appTitle: "Config Generator",
    resetDefaults: "Reset Defaults",
    globalSettings: "Global Settings",
    defaultShipping: "Default Shipping Cost",
    excludeKeywords: "Exclude Keywords",
    addKeywordPlaceholder: "Add custom keyword...",
    add: "Add",
    excludeSellers: "Seller Blacklist",
    excludeSellersHelper: "Press Enter to add seller IDs",
    shoppingCart: "Shopping Cart",
    cardLabel: "Card",
    cardName: "Card Name (ZH)",
    cardNamePlaceholder: "e.g. 原始生命態 尼比魯",
    quantity: "Quantity",
    targetIds: "Target IDs",
    targetIdsPlaceholder: "e.g. QCAC-JP010",
    targetIdsHelper: "Add acceptable ID variants (Press Enter)",
    addCard: "Add Another Card",
    jsonOutput: "JSON Output (Editable)",
    copy: "Copy",
    copied: "Copied!",
    download: "Download JSON",
    tipTitle: "Tip:",
    tipContent: "Ensure you check the 'Target IDs' against the official database. The generator creates the structure, but accuracy depends on your input.",
    tagInputDefaultPlaceholder: "Type and press Enter...",
    jsonError: "Invalid JSON",
    jsonValid: "Valid JSON",
    jsonEditHint: "You can paste or edit JSON here directly to update the UI.",
    fileNamePlaceholder: "Filename"
  }
};

// Default initial state
const initialSettings: GlobalSettings = {
  default_shipping_cost: 60,
  global_exclude_keywords: [...PRESET_KEYWORDS],
  global_exclude_seller: ["19319587", "12987125"]
};

type Language = 'zh' | 'en';

const App: React.FC = () => {
  const [lang, setLang] = useState<Language>('zh');
  const [settings, setSettings] = useState<GlobalSettings>(initialSettings);
  
  // Track all available keyword options, starting with presets
  const [availableKeywords, setAvailableKeywords] = useState<string[]>(PRESET_KEYWORDS);
  const [newKeywordInput, setNewKeywordInput] = useState('');
  
  const [cartItems, setCartItems] = useState<CartItemInternal[]>([
    {
      id: crypto.randomUUID(),
      card_name_zh: "",
      required_amount: 1, // Default to 1
      target_ids: []
    }
  ]);
  const [copied, setCopied] = useState(false);
  const [fileName, setFileName] = useState('cart');

  // JSON Editing State
  const [jsonText, setJsonText] = useState('');
  const [isJsonFocused, setIsJsonFocused] = useState(false);
  const [jsonError, setJsonError] = useState<string | null>(null);

  const t = (key: keyof typeof TRANSLATIONS['zh']) => TRANSLATIONS[lang][key];

  const toggleLanguage = () => {
    setLang(prev => prev === 'zh' ? 'en' : 'zh');
  };

  // -- Handlers for Global Settings --

  const updateSettings = <K extends keyof GlobalSettings>(key: K, value: GlobalSettings[K]) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const toggleKeyword = (keyword: string) => {
    setSettings(prev => {
      const currentKeywords = prev.global_exclude_keywords;
      if (currentKeywords.includes(keyword)) {
        return { 
          ...prev, 
          global_exclude_keywords: currentKeywords.filter(k => k !== keyword) 
        };
      } else {
        return { 
          ...prev, 
          global_exclude_keywords: [...currentKeywords, keyword] 
        };
      }
    });
  };

  const handleRemoveKeyword = (keywordToRemove: string) => {
    setAvailableKeywords(prev => prev.filter(k => k !== keywordToRemove));
    // Also remove from selected list if it's there
    if (settings.global_exclude_keywords.includes(keywordToRemove)) {
      setSettings(prev => ({
        ...prev,
        global_exclude_keywords: prev.global_exclude_keywords.filter(k => k !== keywordToRemove)
      }));
    }
  };

  const handleAddCustomKeyword = () => {
    const trimmed = newKeywordInput.trim();
    if (!trimmed) return;

    // Add to available options if not present
    if (!availableKeywords.includes(trimmed)) {
      setAvailableKeywords(prev => [...prev, trimmed]);
    }

    // Automatically check the new keyword
    if (!settings.global_exclude_keywords.includes(trimmed)) {
      updateSettings('global_exclude_keywords', [...settings.global_exclude_keywords, trimmed]);
    }
    
    setNewKeywordInput('');
  };

  const handleKeywordInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddCustomKeyword();
    }
  };

  // -- Handlers for Shopping Cart --

  const addCartItem = () => {
    setCartItems(prev => [
      ...prev,
      {
        id: crypto.randomUUID(),
        card_name_zh: "",
        required_amount: 1, // Default to 1
        target_ids: []
      }
    ]);
  };

  const removeCartItem = (id: string) => {
    setCartItems(prev => prev.filter(item => item.id !== id));
  };

  const updateCartItem = <K extends keyof CartItemInternal>(
    id: string, 
    field: K, 
    value: CartItemInternal[K]
  ) => {
    setCartItems(prev => prev.map(item => {
      if (item.id === id) {
        return { ...item, [field]: value };
      }
      return item;
    }));
  };

  // Generalized Number Handler with Increment/Decrement support
  const handleNumberChange = (
    val: string | number, 
    setter: (num: number) => void,
    min: number = 0
  ) => {
    let num: number;
    if (typeof val === 'string') {
       if (val === '') {
         setter(0);
         return;
       }
       num = parseInt(val, 10);
    } else {
      num = val;
    }

    if (!isNaN(num)) {
      setter(Math.max(min, num));
    }
  };

  const loadDemoData = () => {
    setSettings({
      default_shipping_cost: 60,
      global_exclude_keywords: [...PRESET_KEYWORDS],
      global_exclude_seller: ["19319587", "12987125"]
    });
    setAvailableKeywords([...PRESET_KEYWORDS]);
    setCartItems([
      {
        id: crypto.randomUUID(),
        card_name_zh: "原始生命態 尼比魯",
        required_amount: 1, // Changed to 1
        target_ids: ["QCAC-JP010", "TTP1-JPB08", "CH01-JP017"]
      },
      {
        id: crypto.randomUUID(),
        card_name_zh: "拮抗勝負",
        required_amount: 1, // Changed to 1
        target_ids: ["RC04-JP075", "SD39-JP039"]
      }
    ]);
    setFileName('cart');
  };

  // -- Output Generation & Bidirectional Logic --

  // Compute the JSON string from current state
  const jsonOutputString = useMemo(() => {
    const cleanCart = cartItems.map(({ id, ...rest }) => rest);
    const output: OutputJson = {
      global_settings: settings,
      shopping_cart: cleanCart
    };
    return JSON.stringify(output, null, 2);
  }, [settings, cartItems]);

  // Sync state to text area when NOT editing
  useEffect(() => {
    if (!isJsonFocused) {
      setJsonText(jsonOutputString);
      setJsonError(null);
    }
  }, [jsonOutputString, isJsonFocused]);

  // Handle manual JSON input
  const handleJsonChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newVal = e.target.value;
    setJsonText(newVal);

    try {
      const parsed = JSON.parse(newVal) as OutputJson;
      
      // Basic schema validation
      if (!parsed.global_settings || !Array.isArray(parsed.shopping_cart)) {
        throw new Error("Missing required fields");
      }

      setJsonError(null);

      // 1. Update Global Settings
      setSettings(prev => ({
        ...prev,
        ...parsed.global_settings
      }));

      // 2. Sync Available Keywords
      // If the pasted JSON has keywords not in our available list, add them.
      if (parsed.global_settings.global_exclude_keywords) {
        setAvailableKeywords(prev => {
          const unique = new Set([...prev, ...parsed.global_settings.global_exclude_keywords]);
          return Array.from(unique);
        });
      }

      // 3. Update Cart Items
      // We need to assign internal IDs to the imported items
      setCartItems(parsed.shopping_cart.map(item => ({
        ...item,
        id: crypto.randomUUID()
      })));

    } catch (err) {
      setJsonError(t('jsonError'));
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(jsonText); // Copy current text content
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy', err);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([jsonText], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    const cleanFileName = fileName.trim() || 'cart';
    const finalFileName = cleanFileName.endsWith('.json') ? cleanFileName : `${cleanFileName}.json`;
    link.download = finalFileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 pb-20">
      
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 text-indigo-600">
            <FileJson size={28} />
            <h1 className="text-xl font-bold tracking-tight text-slate-900">{t('appTitle')}</h1>
          </div>
          
          <div className="flex items-center gap-4">
            <button 
              onClick={toggleLanguage}
              className="text-sm font-medium text-slate-600 hover:text-indigo-600 flex items-center gap-1.5 px-3 py-1.5 rounded-md hover:bg-slate-100 transition-colors"
            >
              <Languages size={16} />
              {lang === 'zh' ? 'English' : '繁體中文'}
            </button>
            
            <button 
              onClick={loadDemoData}
              className="text-sm text-slate-500 hover:text-indigo-600 flex items-center gap-1 transition-colors"
            >
              <RotateCcw size={14} />
              {t('resetDefaults')}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Column: Inputs */}
          <div className="lg:col-span-7 space-y-8">
            
            {/* Section: Global Settings */}
            <section className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center gap-2">
                <Settings className="text-indigo-500" size={20} />
                <h2 className="font-semibold text-lg text-slate-800">{t('globalSettings')}</h2>
              </div>
              
              <div className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    {t('defaultShipping')}
                  </label>
                  <div className="flex items-center gap-2 max-w-xs">
                    <button 
                      onClick={() => handleNumberChange(settings.default_shipping_cost - 10, (val) => updateSettings('default_shipping_cost', val))}
                      className="p-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-600 transition-colors"
                    >
                      <Minus size={16} />
                    </button>
                    <div className="relative flex-1">
                      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">$</span>
                      <input
                        type="number"
                        min="0"
                        value={settings.default_shipping_cost.toString()} 
                        onChange={(e) => handleNumberChange(e.target.value, (val) => updateSettings('default_shipping_cost', val))}
                        onFocus={(e) => e.target.select()}
                        className="w-full pl-7 pr-3 py-2 bg-white text-center text-slate-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all font-mono"
                      />
                    </div>
                    <button 
                      onClick={() => handleNumberChange(settings.default_shipping_cost + 10, (val) => updateSettings('default_shipping_cost', val))}
                      className="p-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-600 transition-colors"
                    >
                      <Plus size={16} />
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    {t('excludeKeywords')}
                  </label>
                  
                  {/* Compact Checkbox List */}
                  <div className="flex flex-wrap gap-2 mb-3">
                    {availableKeywords.map(keyword => (
                      <div 
                        key={keyword} 
                        className={`
                          group flex items-center gap-1 px-2 py-1 rounded-md border text-xs transition-all select-none
                          ${settings.global_exclude_keywords.includes(keyword) 
                            ? 'bg-blue-50 border-blue-200 text-blue-700 font-medium' 
                            : 'bg-white border-slate-200 text-slate-500 hover:bg-slate-50'}
                        `}
                      >
                        <label className="flex items-center gap-1.5 cursor-pointer flex-1">
                          <input
                            type="checkbox"
                            className="w-3.5 h-3.5 text-blue-600 rounded focus:ring-blue-500 border-gray-300"
                            checked={settings.global_exclude_keywords.includes(keyword)}
                            onChange={() => toggleKeyword(keyword)}
                          />
                          <span>{keyword}</span>
                        </label>
                        <button
                          type="button"
                          onClick={() => handleRemoveKeyword(keyword)}
                          className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-red-100 hover:text-red-600 text-slate-400 rounded transition-all focus:opacity-100 focus:outline-none"
                          title="Remove keyword"
                        >
                          <X size={12} />
                        </button>
                      </div>
                    ))}
                  </div>

                  {/* Add New Keyword Input */}
                  <div className="flex gap-2">
                    <input 
                      type="text" 
                      value={newKeywordInput}
                      onChange={(e) => setNewKeywordInput(e.target.value)}
                      onKeyDown={handleKeywordInputKeyDown}
                      placeholder={t('addKeywordPlaceholder')}
                      className="flex-1 px-3 py-1.5 bg-white text-slate-900 border border-slate-300 rounded-md text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <button
                      type="button"
                      onClick={handleAddCustomKeyword}
                      disabled={!newKeywordInput.trim()}
                      className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 text-slate-700 rounded-md text-xs font-medium transition-colors"
                    >
                      {t('add')}
                    </button>
                  </div>
                </div>

                <TagInput
                  label={t('excludeSellers')}
                  helperText={t('excludeSellersHelper')}
                  placeholder={t('tagInputDefaultPlaceholder')}
                  tags={settings.global_exclude_seller}
                  onChange={(tags) => updateSettings('global_exclude_seller', tags)}
                />
              </div>
            </section>

            {/* Section: Shopping Cart */}
            <section className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShoppingCart className="text-indigo-500" size={24} />
                  <h2 className="font-bold text-xl text-slate-800">{t('shoppingCart')}</h2>
                  <span className="bg-indigo-100 text-indigo-700 text-xs font-bold px-2.5 py-0.5 rounded-full">
                    {cartItems.length}
                  </span>
                </div>
              </div>

              <div className="space-y-4">
                {cartItems.map((item, index) => (
                  <div 
                    key={item.id} 
                    className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:border-indigo-300 transition-colors group"
                  >
                    <div className="bg-slate-50 px-4 py-3 border-b border-slate-100 flex justify-between items-center">
                      <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                        {t('cardLabel')} #{index + 1}
                      </span>
                      <button 
                        onClick={() => removeCartItem(item.id)}
                        className="text-slate-400 hover:text-red-500 transition-colors p-1"
                        title="Remove Card"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>

                    <div className="p-5 grid grid-cols-1 md:grid-cols-12 gap-6">
                      {/* Card Name & Amount */}
                      <div className="md:col-span-5 space-y-4">
                        <div>
                          <label className="block text-xs font-medium text-slate-500 mb-1">
                            {t('cardName')}
                          </label>
                          <input
                            type="text"
                            placeholder={t('cardNamePlaceholder')}
                            value={item.card_name_zh}
                            onChange={(e) => updateCartItem(item.id, 'card_name_zh', e.target.value)}
                            className="w-full px-3 py-2 bg-white text-slate-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-slate-500 mb-1">
                            {t('quantity')}
                          </label>
                          <div className="flex items-center gap-2">
                            <button 
                              onClick={() => handleNumberChange(item.required_amount - 1, (val) => updateCartItem(item.id, 'required_amount', val), 1)}
                              className="p-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-600 transition-colors disabled:opacity-50"
                              disabled={item.required_amount <= 1}
                            >
                              <Minus size={16} />
                            </button>
                            <input
                              type="number"
                              min="1"
                              value={item.required_amount.toString()}
                              onChange={(e) => handleNumberChange(e.target.value, (val) => updateCartItem(item.id, 'required_amount', val), 1)}
                              onFocus={(e) => e.target.select()}
                              className="w-full px-3 py-2 bg-white text-center text-slate-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                            />
                            <button 
                              onClick={() => handleNumberChange(item.required_amount + 1, (val) => updateCartItem(item.id, 'required_amount', val), 1)}
                              className="p-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-600 transition-colors"
                            >
                              <Plus size={16} />
                            </button>
                          </div>
                        </div>
                      </div>

                      {/* Target IDs */}
                      <div className="md:col-span-7">
                        <TagInput
                          label={t('targetIds')}
                          placeholder={t('targetIdsPlaceholder')}
                          tags={item.target_ids}
                          onChange={(tags) => updateCartItem(item.id, 'target_ids', tags)}
                          helperText={t('targetIdsHelper')}
                          transformValue={(val) => val.toUpperCase().replace(/[^A-Z0-9\-\s]/g, '').replace(/\s+/g, '-')}
                          inputProps={{
                            autoComplete: "off",
                            spellCheck: false,
                            style: { imeMode: 'disabled' } as React.CSSProperties
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={addCartItem}
                className="w-full py-4 border-2 border-dashed border-slate-300 rounded-xl text-slate-500 font-medium hover:border-indigo-500 hover:text-indigo-600 hover:bg-indigo-50 transition-all flex items-center justify-center gap-2"
              >
                <Plus size={20} />
                {t('addCard')}
              </button>
            </section>
          </div>

          {/* Right Column: Output Preview */}
          <div className="lg:col-span-5">
            <div className="sticky top-24 space-y-4">
              <div className="bg-slate-900 rounded-xl shadow-lg overflow-hidden flex flex-col h-[calc(100vh-8rem)]">
                <div className="flex flex-col sm:flex-row items-center justify-between px-4 py-3 bg-slate-800 border-b border-slate-700 gap-3">
                  <div className="flex items-center gap-3 w-full sm:w-auto">
                    <span className="text-slate-200 font-medium text-sm flex items-center gap-2">
                      <FileJson size={16} /> {t('jsonOutput')}
                    </span>
                    
                    {/* Filename Input */}
                    <div className="flex items-center bg-slate-900/50 rounded border border-slate-600 overflow-hidden ml-2 max-w-[140px] transition-all focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500/50">
                      <input 
                        type="text"
                        value={fileName}
                        onChange={(e) => setFileName(e.target.value)}
                        placeholder="cart"
                        className="bg-transparent text-slate-300 text-xs px-2 py-1 outline-none w-full min-w-0"
                      />
                      <span className="text-slate-500 text-xs pr-2 select-none">.json</span>
                    </div>
                  </div>

                  <div className="flex gap-2 self-end sm:self-auto">
                    <button
                      onClick={handleCopy}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium rounded-md transition-colors"
                    >
                      {copied ? t('copied') : (
                        <>
                          <Copy size={14} /> {t('copy')}
                        </>
                      )}
                    </button>
                    <button
                      onClick={handleDownload}
                      className="p-1.5 text-slate-400 hover:text-white transition-colors"
                      title={t('download')}
                    >
                      <Download size={16} />
                    </button>
                  </div>
                </div>
                
                {/* Editable Text Area */}
                <div className="relative flex-1 bg-slate-900 flex flex-col">
                  <textarea
                    value={jsonText}
                    onChange={handleJsonChange}
                    onFocus={() => setIsJsonFocused(true)}
                    onBlur={() => setIsJsonFocused(false)}
                    className="flex-1 w-full h-full p-4 bg-slate-900 text-emerald-400 font-mono text-xs sm:text-sm leading-relaxed resize-none focus:outline-none custom-scrollbar"
                    spellCheck="false"
                  />
                  
                  {/* Status Indicator Overlay */}
                  <div className={`
                    absolute bottom-4 right-4 px-3 py-1.5 rounded-full text-xs font-medium flex items-center gap-1.5 backdrop-blur-sm transition-all
                    ${jsonError ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 opacity-0 hover:opacity-100'}
                  `}>
                    {jsonError ? (
                      <>
                        <AlertCircle size={14} />
                        {jsonError}
                      </>
                    ) : (
                      <>
                        <CheckCircle2 size={14} />
                        {t('jsonValid')}
                      </>
                    )}
                  </div>
                </div>
                
                <div className="bg-slate-800 px-4 py-2 border-t border-slate-700 text-xs text-slate-400">
                  {t('jsonEditHint')}
                </div>
              </div>
              
              <div className="bg-blue-50 text-blue-800 p-4 rounded-lg text-sm border border-blue-100">
                <p>
                  <strong>{t('tipTitle')}</strong> {t('tipContent')}
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;