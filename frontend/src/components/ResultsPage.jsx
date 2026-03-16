import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Loader2, ExternalLink, Package, AlertCircle } from 'lucide-react';
import api from '../lib/api';

const ResultsPage = () => {
    const { projectId } = useParams();
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchResults = async () => {
            try {
                const res = await api.get(`/projects/${projectId}/results`);
                setResults(res.data);
            } catch (err) {
                console.error("Failed to fetch results", err);
                setError(err.response?.status === 404 ? '尚未找到爬蟲結果，請先執行專案。' : '載入結果失敗');
            } finally {
                setLoading(false);
            }
        };
        fetchResults();
    }, [projectId]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="animate-spin text-primary mb-4" size={48} />
                <p className="text-text-muted">載入結果中...</p>
            </div>
        );
    }

    if (error || !results) {
        return (
            <div className="max-w-4xl mx-auto py-10">
                <div className="flex items-center gap-4 mb-8">
                    <Link to={`/project/${projectId}`} className="p-2 hover:bg-slate-700 rounded-full transition-colors text-text-muted hover:text-white">
                        <ArrowLeft size={24} />
                    </Link>
                    <h1 className="text-2xl font-bold">爬蟲結果（{projectId}）</h1>
                </div>
                <div className="bg-surface border border-slate-700 rounded-xl p-12 text-center flex flex-col items-center">
                    <AlertCircle size={48} className="text-danger/50 mb-4" />
                    <h2 className="text-xl font-bold text-white mb-2">無法顯示結果</h2>
                    <p className="text-text-muted">{error || '發生未知錯誤'}</p>
                    <Link to={`/project/${projectId}`} className="mt-6 bg-primary/20 text-primary hover:bg-primary hover:text-white px-6 py-2 rounded-lg font-medium transition-colors">
                        返回專案
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto space-y-6 pb-20">
            {/* 頂部導覽 */}
            <div className="flex items-center gap-4 mb-8">
                <Link to={`/project/${projectId}`} className="p-2 hover:bg-slate-700 rounded-full transition-colors text-text-muted hover:text-white border border-slate-700 bg-surface">
                    <ArrowLeft size={24} />
                </Link>
                <div className="flex-1">
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <Package className="text-primary" />
                        最佳購買方案
                    </h1>
                    <p className="text-text-muted text-sm mt-1 mb-0">專案：{projectId}</p>
                </div>
            </div>

            {/* 總結區塊 */}
            <div className="bg-gradient-to-br from-indigo-900/40 to-slate-900 border border-indigo-500/30 rounded-xl p-6 shadow-xl mb-8">
                <div className="flex flex-wrap items-center justify-between gap-6">
                    <div>
                        <h2 className="text-text-muted font-medium mb-1">估計總花費 (含運費)</h2>
                        <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
                            NT$ {results.total_cost}
                        </div>
                    </div>
                    <div className="flex gap-8 text-center bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                        <div>
                            <div className="text-text-muted text-sm mb-1">總卡片花費</div>
                            <div className="text-xl font-bold text-white">NT$ {results.total_item_cost}</div>
                        </div>
                        <div className="w-px bg-slate-800"></div>
                        <div>
                            <div className="text-text-muted text-sm mb-1">總運費</div>
                            <div className="text-xl font-bold text-rose-400">NT$ {results.total_shipping_cost}</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* 缺失卡片提示 */}
            {results.missing_cards && results.missing_cards.length > 0 && (
                <div className="bg-rose-900/20 border border-rose-500/30 rounded-xl p-6 mb-8">
                    <h3 className="text-lg font-bold text-rose-400 mb-3 flex items-center gap-2">
                        <AlertCircle size={20} />
                        無法找到最佳組合的卡片 ({results.missing_cards.length})
                    </h3>
                    <div className="flex flex-wrap gap-2">
                        {results.missing_cards.map((cardName, i) => (
                            <span key={i} className="bg-rose-950 text-rose-300 border border-rose-800/50 px-3 py-1 rounded text-sm font-medium">
                                {cardName}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* 賣家列表 (計畫內容) */}
            <div className="space-y-6">
                <h3 className="text-xl font-bold text-white pl-2 border-l-4 border-primary">賣家訂單清單 ({results.plan.length})</h3>

                {results.plan.map((seller, idx) => (
                    <div key={idx} className="bg-surface border border-slate-700 rounded-xl overflow-hidden shadow-lg hover:border-slate-500 transition-colors">
                        <div className="bg-slate-800/80 p-4 border-b border-slate-700 flex flex-wrap justify-between items-center gap-4">
                            <div>
                                <h4 className="text-lg font-bold text-white mb-1"><span className="text-primary mr-2">#{idx + 1}</span> {seller.seller}</h4>
                                <div className="text-sm text-text-muted">小計: <span className="text-emerald-400 font-bold ml-1">NT$ {seller.subtotal}</span></div>
                            </div>
                            <div className="text-sm bg-slate-900 px-4 py-2 rounded-lg border border-slate-700">
                                <span className="text-text-muted mr-3">商品: <span className="text-white font-medium">{seller.items.length}件</span></span>
                                <span className="text-text-muted">運費: <span className="text-rose-400 font-medium">NT$ {seller.shipping_cost}</span></span>
                            </div>
                        </div>

                        <div className="divide-y divide-slate-800/50">
                            {seller.items.map((item, itemIdx) => (
                                <div key={itemIdx} className="p-4 hover:bg-slate-800/30 transition-colors flex items-center gap-4">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <a href={item.url} target="_blank" rel="noopener noreferrer" className="font-bold text-white hover:text-primary transition-colors flex items-center gap-1.5 truncate">
                                                {item.name}
                                                <ExternalLink size={14} className="opacity-50" />
                                            </a>
                                        </div>
                                        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-text-muted">
                                            <span>需求卡片: <span className="text-slate-300 font-medium">{item.card_name_zh}</span></span>
                                            <span>單價: NT$ {item.price}</span>
                                            <span>數量: <span className="text-white font-bold">{item.buy_count}</span></span>
                                            <span className="font-mono bg-slate-900 border border-slate-700 px-1.5 py-0.5 rounded text-xs">{item.card_number}</span>
                                        </div>
                                    </div>
                                    <div className="text-right flex-shrink-0">
                                        <div className="font-bold text-emerald-400">NT$ {item.price * item.buy_count}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            <div className="mt-8 text-center">
                <Link to={`/project/${projectId}`} className="inline-flex items-center gap-2 text-text-muted hover:text-white hover:underline transition-all">
                    <ArrowLeft size={16} /> 返回專案購物車
                </Link>
            </div>
        </div>
    );
};

export default ResultsPage;
