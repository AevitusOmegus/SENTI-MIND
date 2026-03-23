import { useEffect } from "react";

export default function InsightModal({ insight, onClose }) {
  useEffect(() => {
    const handler = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  if (!insight) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm animate-fade-in"
      onClick={onClose}
    >
      <div
        className="glass-card-deep relative w-full max-w-lg mx-4 p-7 animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close */}
        <button
          id="close-insight-modal"
          onClick={onClose}
          aria-label="Close modal"
          className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full bg-sage-100 text-sage-700 hover:bg-sage-200 transition-colors text-sm font-bold"
        >
          ✕
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-sage-300 to-sage-400 flex items-center justify-center text-white text-base shadow-sm">
            💡
          </div>
          <div>
            <h2 className="text-base font-700 text-sage-700 leading-tight">
              AI Insight
            </h2>
            <p className="text-xs text-sage-500">Powered by SentiMind</p>
          </div>
        </div>

        <div className="h-px bg-sage-200 mb-4" />

        {/* Structured Content Render */}
        <div className="content-container">
          {(() => {
            if (!insight) return null;
            
            const hasInsight = insight.includes("**Insight:**");
            const hasCoping = insight.includes("**Coping Strategies:**");
            
            if (hasInsight && hasCoping) {
              const parts = insight.split("**Coping Strategies:**");
              const insightPart = parts[0].replace("**Insight:**", "").trim();
              const copingPart = parts[1] ? parts[1].trim() : "";
              
              const copingLines = copingPart.split("\n").filter(line => line.trim() !== "");
              
              return (
                <div className="space-y-5">
                  <div className="bg-sage-50/60 border border-sage-100 rounded-2xl p-5 shadow-inner relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-sage-200 to-transparent opacity-30 rounded-bl-full" />
                    <p className="text-sm leading-relaxed text-[#2E7D32] relative z-10 font-medium whitespace-pre-line">
                      {insightPart.replace(/\*\*(.*?)\*\*/g, '$1')}
                    </p>
                  </div>
                  
                  {copingLines.length > 0 && (
                    <div className="pt-1">
                      <h3 className="text-sage-700 font-bold text-[13px] uppercase tracking-wider mb-4 flex items-center gap-2">
                        <span className="w-6 h-6 rounded-md bg-sage-200 flex justify-center items-center text-xs shadow-sm">🌱</span>
                        Actionable Strategies
                      </h3>
                      <ul className="space-y-3 pl-1 text-sm text-[#3a7c3f]">
                        {copingLines.map((line, idx) => {
                          const cleanLine = line.replace(/^(\d+\.|-|\*)\s*/, "").replace(/\*\*(.*?)\*\*/g, '$1').trim();
                          if (!cleanLine) return null;
                          return (
                            <li key={idx} className="flex items-start gap-3 group">
                              <span className="w-1.5 h-1.5 rounded-full bg-sage-400 mt-1.5 flex-shrink-0 group-hover:scale-150 group-hover:bg-sage-600 transition-all duration-300" />
                              <span className="leading-relaxed font-medium opacity-90">{cleanLine}</span>
                            </li>
                          );
                        })}
                      </ul>
                    </div>
                  )}
                </div>
              );
            }
            
            // Fallback for non-standard generation
            return (
              <p className="text-sm leading-relaxed text-[#2E7D32] whitespace-pre-line">
                {insight.replace(/\*\*(.*?)\*\*/g, '$1')}
              </p>
            );
          })()}
        </div>

        <button
          onClick={onClose}
          className="btn-sage mt-5 w-full py-2.5 text-sm"
        >
          Got it
        </button>
      </div>
    </div>
  );
}
