'use client';

import { useState, useEffect } from 'react';
import { useLocale } from 'next-intl';
import { Sparkles, X, RefreshCw, AlertTriangle, Lightbulb, PackageSearch, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import api from '@/lib/api';

export default function AIFloatingButton() {
  const locale = useLocale();
  const [open, setOpen] = useState(false);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchInsights = async () => {
    setLoading(true);
    setError('');
    try {
      // 1. Get business context
      const ctxRes = await api.get('/reports/ai-context');
      const { products, summary } = ctxRes.data;

      if (!products?.length && (!summary || summary.sales === 0)) {
        setData({ isNew: true });
        return;
      }

      // 2. Fetch AI insights through local proxy or direct if stable
      const res = await fetch('/api/ai-insights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ products, summary, locale }),
      });
      
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || 'Failed to fetch insights');
      setData(json);
    } catch (e: any) {
      setError(e.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Trigger Button */}
      <button
        onClick={() => { setOpen(!open); if(!open && !data) fetchInsights(); }}
        className={cn(
          'fixed bottom-6 right-6 z-50 flex items-center gap-2 px-5 py-3 rounded-2xl shadow-2xl transition-all duration-300',
          open 
            ? 'bg-slate-800 text-slate-400 border border-slate-700 pointer-events-auto' 
            : 'bg-indigo-600 hover:bg-indigo-500 text-white border border-indigo-400/30'
        )}
      >
        {open ? <X size={18} /> : <Sparkles size={18} />}
        <span className="font-bold text-sm">AI Expert</span>
      </button>

      {/* Side Panel */}
      <div className={cn(
        'fixed top-0 right-0 h-full w-[400px] max-w-[90vw] bg-slate-950 border-l border-slate-800 z-40 shadow-2xl transition-transform duration-500 ease-out flex flex-col',
        open ? 'translate-x-0' : 'translate-x-full'
      )}>
        <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
          <div className="flex items-center gap-2">
            <Sparkles size={20} className="text-indigo-400" />
            <h2 className="text-lg font-bold text-white tracking-tight">AI Insights</h2>
          </div>
          <button onClick={() => setOpen(false)} className="text-slate-500 hover:text-white transition-colors">
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading && (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
              <RefreshCw className="animate-spin text-indigo-500" size={32} />
              <p className="text-sm font-medium text-slate-400">Analyzing your business...</p>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
              <p className="text-xs text-red-400 font-medium">{error}</p>
              <button 
                onClick={fetchInsights}
                className="mt-3 text-[10px] font-bold uppercase tracking-widest text-red-400 hover:text-red-300 transition-colors"
              >
                Try Again
              </button>
            </div>
          )}

          {data?.isNew && (
            <div className="text-center py-10 space-y-4">
              <div className="w-16 h-16 bg-emerald-500/10 rounded-2xl flex items-center justify-center mx-auto">
                <PackageSearch className="text-emerald-500" size={32} />
              </div>
              <h3 className="text-white font-bold">Welcome!</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Add products and start selling to unlock AI insights tailored to your store.
              </p>
            </div>
          )}

          {data && !data.isNew && !loading && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {/* Profit Summary */}
              {data.profitAnalysis && (
                <div className="p-5 bg-indigo-500/5 border border-indigo-500/10 rounded-2xl space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Performance</span>
                    <TrendingUp size={14} className="text-emerald-500" />
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed font-medium">
                    {data.profitAnalysis.yesterday?.summary || 'Stable sales recorded yesterday.'}
                  </p>
                </div>
              )}

              {/* Suggestions */}
              {data.suggestions?.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-xs font-black text-slate-500 uppercase tracking-widest px-1">Smart Suggestions</h4>
                  <div className="space-y-3">
                    {data.suggestions.map((s: any, i: number) => (
                      <div key={i} className="p-4 bg-slate-900 border border-slate-800 rounded-xl hover:border-slate-700 transition-colors group">
                        <div className="flex items-center gap-2 mb-2">
                          <Lightbulb size={14} className="text-amber-400" />
                          <span className="text-xs font-bold text-slate-200">{s.title}</span>
                          <span className={cn(
                            'ml-auto text-[9px] font-bold px-1.5 py-0.5 rounded uppercase',
                            s.impact === 'high' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-blue-500/20 text-blue-400'
                          )}>
                            {s.impact}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 leading-relaxed group-hover:text-slate-400 transition-colors">
                          {s.detail}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {!data && !loading && !error && (
            <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
              <Sparkles size={40} className="text-slate-700" />
              <p className="text-sm text-slate-500 max-w-[200px]">
                Click 'Analyze' to get personalized business tips.
              </p>
              <button 
                onClick={fetchInsights}
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-xl font-bold text-sm transition-all"
              >
                Analyze Now
              </button>
            </div>
          )}
        </div>

        <div className="p-6 border-t border-slate-800 bg-slate-900/30">
          <p className="text-[10px] text-center text-slate-600 font-medium">
            AI can make mistakes. Always verify critical business data.
          </p>
        </div>
      </div>
    </>
  );
}
