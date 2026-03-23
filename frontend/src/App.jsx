import { useState } from "react";
import { useAnalysis } from "./hooks/useAnalysis";
import EmotionChart from "./components/EmotionChart";
import RiskBadge from "./components/RiskBadge";
import InsightModal from "./components/InsightModal";

const CATEGORY_CONFIG = {
  Normal:               { color: "text-sage-700",   bg: "bg-sage-100",   border: "border-sage-300",   icon: "🌿", label: "Normal" },
  Stress:               { color: "text-amber-600",  bg: "bg-amber-50",   border: "border-amber-300",  icon: "🌅", label: "Stress" },
  Anxiety:              { color: "text-orange-500", bg: "bg-orange-50",  border: "border-orange-300", icon: "⚡", label: "Anxiety" },
  Bipolar:              { color: "text-indigo-400", bg: "bg-indigo-50",  border: "border-indigo-300", icon: "🌊", label: "Bipolar" },
  Depression:           { color: "text-rose-500",   bg: "bg-rose-50",    border: "border-rose-300",   icon: "☁️", label: "Depression" },
  Suicidal:             { color: "text-rose-600",   bg: "bg-rose-50",    border: "border-rose-400",   icon: "🚨", label: "Suicidal" },
  "Personality Disorder": { color: "text-violet-600", bg: "bg-violet-50", border: "border-violet-300", icon: "🎭", label: "Personality Disorder" },
};

const DEFAULT_CAT = { color: "text-sage-700", bg: "bg-sage-100", border: "border-sage-300", icon: "💬", label: "Unknown" };

export default function App() {
  const [text, setText] = useState("");
  const [showInsight, setShowInsight] = useState(false);
  const { result, loading, error, analyze, reset } = useAnalysis();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim()) analyze(text);
  };

  const handleReset = () => {
    setText("");
    setShowInsight(false);
    reset();
  };

  const catCfg = result
    ? (CATEGORY_CONFIG[result.clinical.category] ?? DEFAULT_CAT)
    : null;

  return (
    <div className="min-h-screen flex flex-col">
      <header className="w-full py-2">
        <nav className="mx-auto max-w-3xl px-4 py-3 glass-card flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">🧠</span>
            <span className="font-extrabold text-lg text-sage-700 tracking-tight">
              Senti<span className="text-sage-400">Mind</span>
            </span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-xs font-medium text-sage-500 bg-sage-100 border border-sage-200 px-3 py-1 rounded-full">
              AI Analysis
            </span>
          </div>
        </nav>
      </header>

      <main className="flex-1 flex flex-col items-center px-4 pt-6 pb-16">
        {/* Hero */}
        <div className="text-center mb-8 animate-fade-in">
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-sage-700 leading-tight">
            What's on your
            <span className="block bg-gradient-to-r from-sage-400 to-sage-700 bg-clip-text text-transparent pb-1">
              mind today?
            </span>
          </h1>
          <p className="mt-3 text-sm text-sage-500 max-w-md mx-auto leading-relaxed">
            Share your thoughts — our AI gently analyses emotions, clinical patterns, and risk with empathy.
          </p>
        </div>

        {/* Input card */}
        <form onSubmit={handleSubmit} className="w-full max-w-2xl animate-slide-up">
          <div className="glass-card-deep p-5">
            <label className="section-label block mb-2" htmlFor="analysis-input">
              Your thoughts
            </label>
            <textarea
              id="analysis-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Start writing freely — this is your safe space…"
              rows={6}
              className="w-full rounded-xl bg-sage-100/60 border border-sage-200 px-4 py-3 text-sm text-sage-700 placeholder:text-sage-400 resize-none focus:outline-none focus:ring-2 focus:ring-sage-300 transition leading-relaxed"
            />

            <div className="flex gap-3 mt-4">
              <button
                id="analyze-btn"
                type="submit"
                disabled={loading || !text.trim()}
                className="btn-sage flex-1 py-3 text-sm"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
                    Analysing…
                  </span>
                ) : (
                  "✦ Analyse"
                )}
              </button>
              {result && (
                <button
                  id="reset-btn"
                  type="button"
                  onClick={handleReset}
                  className="px-5 rounded-xl border border-sage-200 text-sm text-sage-500 hover:text-sage-700 hover:border-sage-300 hover:bg-sage-100 transition font-500"
                >
                  Reset
                </button>
              )}
            </div>
          </div>
        </form>

        {/* Error */}
        {error && (
          <div className="mt-4 w-full max-w-2xl glass-card border-rose-300 bg-rose-50 p-4 text-sm text-rose-600 flex items-start gap-2 animate-fade-in">
            <span className="mt-0.5">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="mt-7 w-full max-w-2xl space-y-4 animate-slide-up">

            {/* Clinical category */}
            <div className={`glass-card border p-5 ${catCfg.border} ${catCfg.bg}`}>
              <p className="section-label mb-2">Clinical Category</p>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{catCfg.icon}</span>
                  <div>
                    <p className={`text-2xl font-bold capitalize leading-tight ${catCfg.color}`}>
                      {result.clinical.category}
                    </p>
                    <p className="text-xs text-sage-500 mt-0.5">
                      {(result.clinical.confidence * 100).toFixed(0)}% confidence
                    </p>
                  </div>
                </div>
                {/* Confidence arc */}
                <div className="relative w-14 h-14">
                  <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="15" fill="none" stroke="rgba(165,214,167,0.25)" strokeWidth="3" />
                    <circle
                      cx="18" cy="18" r="15" fill="none"
                      stroke="#4CAF50" strokeWidth="3"
                      strokeDasharray={`${result.clinical.confidence * 94.25} 94.25`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <span className={`absolute inset-0 flex items-center justify-center text-[10px] font-bold ${catCfg.color}`}>
                    {(result.clinical.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              {/* Top categories mini bars */}
              {result.clinical.top_categories.length > 1 && (
                <div className="mt-4 space-y-1.5">
                  {result.clinical.top_categories.slice(0, 4).map((c) => (
                    <div key={c.category} className="flex items-center gap-2">
                      <span className="text-xs w-28 text-sage-600 truncate">{c.category}</span>
                      <div className="flex-1 h-1.5 rounded-full bg-white/60 overflow-hidden">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-sage-300 to-sage-400 transition-all duration-500"
                          style={{ width: `${c.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-sage-500 w-8 text-right">
                        {(c.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Emotion radar */}
            <div className="glass-card p-5">
              <p className="section-label mb-4">Emotion Distribution</p>
              <EmotionChart emotions={result.emotions} />
            </div>

            {/* Risk */}
            <RiskBadge
              level={result.risk.level}
              score={result.risk.score}
              triggers={result.risk.triggers}
              safety_protocol={result.risk.safety_protocol}
            />

            {/* Named entities */}
            {result.entities.length > 0 && (
              <div className="glass-card p-5">
                <p className="section-label mb-3">Named Entities</p>
                <div className="flex flex-wrap gap-2">
                  {result.entities.map((ent, i) => (
                    <span
                      key={i}
                      className="text-xs rounded-full bg-cloud-100 border border-cloud-200 text-indigo-400 font-500 px-3 py-1"
                    >
                      {ent.text}{" "}
                      <span className="opacity-60 text-[10px]">[{ent.label}]</span>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Insight CTA */}
            {result.insight && (
              <button
                id="show-insight-btn"
                onClick={() => setShowInsight(true)}
                className="w-full glass-card border border-sage-300 py-4 flex items-center justify-center gap-3 group hover:bg-sage-100/50 transition-all"
              >
                <span className="w-8 h-8 rounded-lg bg-gradient-to-br from-sage-300 to-sage-400 flex items-center justify-center text-sm shadow-sm group-hover:scale-110 transition-transform">
                  💡
                </span>
                <span className="text-sm font-semibold text-sage-700">
                  View AI Insight
                </span>
                <span className="ml-auto text-sage-400 text-xs">tap to open →</span>
              </button>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="pb-6 text-center">
        <p className="text-xs text-sage-400">SentiMind · AI is not a substitute for professional care</p>
      </footer>

      {showInsight && (
        <InsightModal insight={result?.insight} onClose={() => setShowInsight(false)} />
      )}
    </div>
  );
}
