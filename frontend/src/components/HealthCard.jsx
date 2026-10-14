
function HealthCard({ health }) {
  const score = health?.score ?? 0;
  const status = health?.status ?? "Unknown";

  let scoreColor = "text-red-400";
  let barColor = "bg-red-400";

  if (score >= 90) {
    scoreColor = "text-green-400";
    barColor = "bg-green-400";
  } else if (score >= 75) {
    scoreColor = "text-blue-400";
    barColor = "bg-blue-400";
  } else if (score >= 50) {
    scoreColor = "text-yellow-400";
    barColor = "bg-yellow-400";
  }

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 transition hover:border-slate-700">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-400">
          Network Health
        </p>

        <span
          className={
            "rounded-full bg-slate-800 px-3 py-1 text-xs font-semibold " +
            scoreColor
          }
        >
          {status}
        </span>
      </div>

      <div className="mt-4 flex items-end gap-1">
        <p className={"text-4xl font-bold " + scoreColor}>
          {score}
        </p>

        <span className="mb-1 text-lg text-slate-500">
          /100
        </span>
      </div>

      <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
        <div
          className={
            "h-full rounded-full transition-all duration-700 " +
            barColor
          }
          style={{
            width: `${Math.min(Math.max(score, 0), 100)}%`,
          }}
        />
      </div>

      <div className="mt-3 flex justify-between text-xs text-slate-500">
        <span>0</span>
        <span>50</span>
        <span>100</span>
      </div>
    </div>
  );
}

export default HealthCard;
