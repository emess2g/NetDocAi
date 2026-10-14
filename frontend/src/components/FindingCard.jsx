
function FindingCard({ finding }) {
  let badgeClass = "bg-blue-500/10 text-blue-400";

  if (finding.severity === "critical") {
    badgeClass = "bg-red-500/10 text-red-400";
  } else if (finding.severity === "high") {
    badgeClass = "bg-orange-500/10 text-orange-400";
  } else if (finding.severity === "warning") {
    badgeClass = "bg-yellow-500/10 text-yellow-400";
  } else if (finding.severity === "info") {
    badgeClass = "bg-blue-500/10 text-blue-400";
  }

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-950 p-5">
      <div className="flex items-center justify-between">
        <span
          className={
            "rounded-full px-3 py-1 text-xs font-semibold uppercase " +
            badgeClass
          }
        >
          {finding.severity}
        </span>

        <span className="text-xs uppercase text-slate-500">
          {finding.category}
        </span>
      </div>

      <p className="mt-4 font-medium text-white">
        {finding.finding}
      </p>

      <div className="mt-3 rounded-lg bg-slate-900 p-3">
        <p className="text-xs font-semibold uppercase text-slate-500">
          Recommendation
        </p>

        <p className="mt-1 text-sm text-slate-400">
          {finding.recommendation}
        </p>
      </div>
    </div>
  );
}

export default FindingCard;

