const LEVEL_CONFIG = {
  low: {
    bg: "bg-sage-100",
    border: "border-sage-300",
    text: "text-sage-700",
    dot: "bg-sage-400",
    pill: "bg-sage-200 text-sage-700 border-sage-300",
    label: "Low Risk",
    icon: "🌿",
    bar: "bg-gradient-to-r from-sage-300 to-sage-400",
  },
  medium: {
    bg: "bg-amber-50",
    border: "border-amber-300",
    text: "text-amber-700",
    dot: "bg-amber-300",
    pill: "bg-amber-50 text-amber-700 border-amber-300",
    label: "Moderate",
    icon: "🌅",
    bar: "bg-gradient-to-r from-amber-300 to-amber-400",
  },
  high: {
    bg: "bg-rose-50",
    border: "border-rose-300",
    text: "text-rose-500",
    dot: "bg-rose-300",
    pill: "bg-rose-50 text-rose-500 border-rose-300",
    label: "High Alert",
    icon: "⚡",
    bar: "bg-gradient-to-r from-rose-300 to-rose-400",
  },
  critical: {
    bg: "bg-rose-50",
    border: "border-rose-500",
    text: "text-rose-600",
    dot: "bg-rose-500",
    pill: "bg-rose-100 text-rose-600 border-rose-400",
    label: "CRITICAL",
    icon: "🚨",
    bar: "bg-gradient-to-r from-rose-400 to-rose-500",
  },
};

export default function RiskBadge({ level = "low", score = 0, triggers = [], safety_protocol = false }) {
  const cfg = (safety_protocol || level === "critical")
    ? LEVEL_CONFIG.critical
    : (LEVEL_CONFIG[level] ?? LEVEL_CONFIG.low);

  const pct = Math.round(score * 100);

  return (
    <div className={`glass-card p-5 border ${cfg.border} ${cfg.bg} animate-slide-up`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-lg">{cfg.icon}</span>
          <div>
            <p className="section-label">Risk Assessment</p>
            <p className={`font-700 text-base leading-tight ${cfg.text}`}>
              {cfg.label}
            </p>
          </div>
        </div>
        <div className={`text-2xl font-800 tabular-nums ${cfg.text}`}>
          {pct}%
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full h-2 rounded-full bg-white/70 overflow-hidden mb-3">
        <div
          className={`h-full rounded-full transition-all duration-700 ${cfg.bar}`}
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Safety note */}
      {safety_protocol && (
        <div className="mb-3 flex items-start gap-2 rounded-xl bg-rose-100 border border-rose-300 px-3 py-2">
          <span className="text-rose-500 text-sm mt-0.5">⚠️</span>
          <p className="text-xs text-rose-600 leading-relaxed">
            High clinical risk detected. Please reach out to a trusted person or mental health professional.
          </p>
        </div>
      )}

      {/* Trigger pills */}
      {triggers.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {triggers.map((t) => (
            <span
              key={t}
              className={`text-xs px-2.5 py-0.5 rounded-full border font-500 ${cfg.pill}`}
            >
              {t}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
