import { useState } from "react";
import { Link } from "react-router-dom";
import { useAnalysis } from "../hooks/useAnalysis";
import { saveJournalEntry, saveGratitude } from "../services/journalService";
import { logMood } from "../services/moodService";
import EmotionChart from "../components/EmotionChart";
import RiskBadge from "../components/RiskBadge";
import InsightModal from "../components/InsightModal";
import CrisisAlertBanner from "../components/CrisisAlertBanner";
import GratitudeModal from "../components/GratitudeModal";

const CATEGORY_CONFIG = {
  Normal: { color: "text-sage-700", bg: "bg-sage-50", icon: "🌿", label: "Normal", border: "border-sage-200" },
  Stress: { color: "text-medical-mild", bg: "bg-amber-50", icon: "🌅", label: "Stress", border: "border-amber-200" },
  Anxiety: { color: "text-medical-moderate", bg: "bg-orange-50", icon: "🌊", label: "Anxiety", border: "border-orange-200" },
  Bipolar: { color: "text-indigo-700", bg: "bg-indigo-50", icon: "⚡", label: "Bipolar", border: "border-indigo-200" },
  Depression: { color: "text-medical-severe", bg: "bg-rose-50", icon: "☁️", label: "Depression", border: "border-rose-200" },
  Suicidal: { color: "text-medical-emergency", bg: "bg-rose-100", icon: "🚨", label: "Suicidal", border: "border-rose-300" },
  "Personality Disorder": { color: "text-violet-700", bg: "bg-violet-50", icon: "🎭", label: "Personality Disorder", border: "border-violet-200" },
};

const DEFAULT_CAT = { color: "text-warm-600", bg: "bg-warm-50", icon: "💭", label: "Unknown", border: "border-warm-200" };

export default function JournalPage() {
  const [text, setText] = useState("");
  const [showInsight, setShowInsight] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const [gratitudeStatus, setGratitudeStatus] = useState(null);
  const { result, loading, error, analyze, reset } = useAnalysis();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    
    // 1. Analyze
    const analysisRes = await analyze(text);
    if (!analysisRes) return;

    // 2. Auto-save to Vault and Mood Log
    try {
      setSaveStatus("Saving to vault...");
      const savedEntry = await saveJournalEntry({
        raw_text: text,
        analysis: analysisRes,
        category: analysisRes.clinical.category,
        risk_level: analysisRes.risk.level
      });
      
      await logMood({
        category: analysisRes.clinical.category,
        confidence: analysisRes.clinical.confidence,
        risk_level: analysisRes.risk.level,
        risk_score: analysisRes.risk.score,
        entry_id: savedEntry.id
      });
      
      setSaveStatus("Saved to vault ✓");
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (err) {
      console.error(err);
      setSaveStatus("Failed to save.");
    }
  };

  const handleGratitude = async () => {
    if (!text.trim()) return;
    try {
      await saveGratitude(text);
      setGratitudeStatus("success");
    } catch (err) {
      setGratitudeStatus("error");
    }
  };

  const handleReset = () => {
    setText("");
    setShowInsight(false);
    setSaveStatus(null);
    reset();
  };

  const catCfg = result ? (CATEGORY_CONFIG[result.clinical.category] ?? DEFAULT_CAT) : null;
  const isCritical = result && (result.risk?.level === "critical" || result.clinical?.category === "Suicidal");

  return (
    <div className="space-y-6">
      <div className="mb-2">
        <h1 className="medical-heading-2 text-warm-800 tracking-tight text-2xl sm:text-3xl">Secure Journal</h1>
        <p className="text-warm-500 text-sm mt-1">Reflect. AI will analyze and save your patterns securely.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* LEFT COLUMN: Input & Actionable Insights */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          
          {isCritical && (
            <div className="animate-medical-fade-in">
              <CrisisAlertBanner isVisible={true} category={result?.clinical?.category} confidence={result?.clinical?.confidence} />
              <div className="mt-3 flex flex-wrap gap-2">
                <Link to="/dashboard/wellness" className="medical-btn bg-white border border-rose-200 text-rose-700 hover:bg-rose-100 px-4 py-2 text-sm">
                  🌬️ Box Breathing
                </Link>
                <Link to="/dashboard/wellness" className="medical-btn bg-white border border-rose-200 text-rose-700 hover:bg-rose-100 px-4 py-2 text-sm">
                  🖐️ 5-4-3-2-1 Grounding
                </Link>
              </div>
            </div>
          )}

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="medical-card p-4 sm:p-6 animate-medical-slide-up">
            <label className="medical-label flex justify-between items-center mb-3">
              <span>How are you feeling?</span>
              <span className="text-warm-400 font-normal normal-case text-xs">({text.length} chars)</span>
            </label>
            
            <textarea
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder="Start typing your entry here..."
              rows={6}
              disabled={loading}
              className="medical-input resize-none text-base"
            />

            <div className="flex flex-wrap items-center justify-between gap-3 mt-4">
              <div className="text-sm text-sage-600 font-medium">{saveStatus}</div>
              <div className="flex flex-wrap gap-2 ml-auto">
                {result && result.clinical.category === "Normal" && (
                  <button type="button" onClick={handleGratitude} className="medical-btn medical-btn-secondary py-2 px-3 text-sm shadow-sm">
                    🫙 Add to Jar
                  </button>
                )}
                {result ? (
                  <button type="button" onClick={handleReset} className="medical-btn medical-btn-secondary py-2 px-4 text-sm shadow-sm">New Entry</button>
                ) : (
                  <button type="submit" disabled={loading || !text.trim()} className="medical-btn medical-btn-primary py-2 px-5 text-sm shadow-md">
                    {loading ? "Analyzing..." : "Analyze & Save"}
                  </button>
                )}
              </div>
            </div>
          </form>

          {error && <div className="p-4 bg-rose-50 text-rose-700 rounded-lg">{error}</div>}

          {/* AI Clinical Insight Button - Underneath text */}
          {result?.insight && (
            <div className="medical-card p-6 flex items-center gap-6 hover:bg-sage-50 transition-colors cursor-pointer group animate-medical-fade-in" onClick={() => setShowInsight(true)}>
               <div className="w-16 h-16 rounded-full bg-sage-100 flex-shrink-0 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform shadow-inner border border-sage-200">💡</div>
               <div>
                 <h3 className="font-semibold text-warm-800 text-lg tracking-tight">AI Clinical Insight Generated</h3>
                 <p className="text-sm text-warm-500 mt-1">We've identified actionable patterns tailored specifically to this entry.</p>
                 <span className="inline-flex items-center mt-3 text-sage-600 font-medium text-sm group-hover:underline">Read Detailed Insight <span className="ml-1 group-hover:translate-x-1 transition-transform">→</span></span>
               </div>
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: Analytics Panel */}
        <div className="lg:col-span-1 flex flex-col gap-6 sticky top-8">
           {result ? (
             <div className="space-y-6 animate-medical-fade-in">
               <div className="flex items-center justify-between pb-2 border-b border-sage-200/60">
                 <h3 className="medical-label">Live Analysis</h3>
                 <span className="flex h-2 w-2">
                   <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-sage-400 opacity-75"></span>
                   <span className="relative inline-flex rounded-full h-2 w-2 bg-sage-500"></span>
                 </span>
               </div>
               
               <div className={`medical-card p-5 border-l-4 ${catCfg.border}`}>
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 flex items-center justify-center rounded-xl text-3xl ${catCfg.bg} ${catCfg.color}`}>{catCfg.icon}</div>
                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-wider text-warm-400 mb-0.5">Primary State</p>
                      <h3 className={`text-xl font-bold leading-tight tracking-tight ${catCfg.color}`}>{catCfg.label}</h3>
                      <p className="text-xs text-warm-500 mt-1">Confidence: {(result.clinical.confidence * 100).toFixed(0)}%</p>
                    </div>
                  </div>
               </div>
               
               <RiskBadge level={result.risk.level} score={result.risk.score} triggers={result.risk.triggers} safety_protocol={result.risk.safety_protocol} components={result.risk.components} />

               <div className="medical-card p-5">
                 <p className="text-[10px] font-bold uppercase tracking-wider text-warm-500 mb-4">Emotional Breakdown</p>
                 <EmotionChart emotions={result.emotions} />
               </div>
             </div>
           ) : (
             <div className="h-full min-h-[360px] border-2 border-dashed border-sage-200 rounded-3xl flex flex-col items-center justify-center text-warm-400 p-8 text-center bg-sage-50/50">
               <div className="w-16 h-16 bg-sage-100 rounded-full flex items-center justify-center text-3xl opacity-50 mb-3 shadow-inner">🧭</div>
               <p className="text-sm font-semibold text-warm-600 tracking-tight">Awaiting Entry</p>
               <p className="text-xs mt-2 leading-relaxed">Write your journal entry and analyze it to view your real-time psychological metrics.</p>
             </div>
           )}
        </div>
      </div>

      {showInsight && <InsightModal insight={result?.insight} modelsUsed={result?.models_used} onClose={() => setShowInsight(false)} />}
      <GratitudeModal isOpen={gratitudeStatus !== null} isError={gratitudeStatus === "error"} onClose={() => setGratitudeStatus(null)} />
    </div>
  );
}
