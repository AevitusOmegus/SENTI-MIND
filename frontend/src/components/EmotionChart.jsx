import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

export default function EmotionChart({ emotions }) {
  const data = emotions.map((e) => ({
    emotion: e.label.charAt(0).toUpperCase() + e.label.slice(1),
    score: Math.round(e.score * 100),
  }));

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data}>
          <PolarGrid stroke="rgba(165, 214, 167, 0.5)" />
          <PolarAngleAxis
            dataKey="emotion"
            tick={{ fill: "#2E7D32", fontSize: 11, fontWeight: 500 }}
          />
          <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
          <Radar
            name="Emotion"
            dataKey="score"
            stroke="#4CAF50"
            fill="#81C784"
            fillOpacity={0.3}
            strokeWidth={2}
          />
          <Tooltip
            contentStyle={{
              background: "rgba(255, 255, 255, 0.92)",
              border: "1px solid rgba(165, 214, 167, 0.6)",
              borderRadius: "10px",
              color: "#1B5E20",
              fontSize: "12px",
              boxShadow: "0 4px 16px rgba(46, 125, 50, 0.12)",
            }}
            formatter={(v) => [`${v}%`, "Score"]}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
