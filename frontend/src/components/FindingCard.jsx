function FindingCard({ finding }) {
  const severity = String(finding?.severity || "info").toLowerCase();
  const badgeClasses = {
    critical: "bg-red-500/10 text-red-400",
    high: "bg-orange-500/10 text-orange-400",
    medium: "bg-yellow-500/10 text-yellow-400",
    warning: "bg-yellow-500/10 text-yellow-400",
    low: "bg-blue-500/10 text-blue-400",
    info: "bg-blue-500/10 text-blue-400",
  };
  const evidence = Array.isArray(finding?.evidence)
    ? finding.evidence
    : finding?.evidence
      ? [finding.evidence]
      : [];

  return (
    <article className="rounded-xl border border-slate-700 bg-slate-950 p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <span className={"rounded-full px-3 py-1 text-xs font-semibold uppercase " + (badgeClasses[severity] || badgeClasses.info)}>
          {severity}
        </span>
        <span className="text-xs uppercase tracking-wide text-slate-500">
          {finding?.category || "general"}
        </span>
      </div>

      <p className="mt-4 font-medium leading-6 text-white">
        {finding?.finding || "Unspecified finding"}
      </p>

      {(finding?.device || finding?.timestamp || finding?.event_code) && (
        <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
          {finding?.device && <span>Device: <strong className="font-medium text-slate-300">{finding.device}</strong></span>}
          {finding?.timestamp && <time dateTime={finding.timestamp}>{finding.timestamp}</time>}
          {finding?.event_code && <span className="font-mono text-slate-400">{finding.event_code}</span>}
        </div>
      )}

      {finding?.impact && (
        <div className="mt-4 rounded-lg border border-white/5 bg-white/[0.02] p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Event details / impact</p>
          <p className="mt-1 break-words text-sm leading-6 text-slate-300">{finding.impact}</p>
        </div>
      )}

      {evidence.length > 0 && (
        <div className="mt-3 rounded-lg bg-[#070b12] p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Evidence</p>
          <div className="mt-2 space-y-2">
            {evidence.map((item, index) => (
              <pre key={index} className="overflow-x-auto whitespace-pre-wrap break-words text-xs leading-5 text-slate-400">{typeof item === "string" ? item : JSON.stringify(item, null, 2)}</pre>
            ))}
          </div>
        </div>
      )}

      {finding?.recommendation && (
        <div className="mt-3 rounded-lg bg-slate-900 p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Recommended action</p>
          <p className="mt-1 text-sm leading-6 text-slate-400">{finding.recommendation}</p>
        </div>
      )}

      {finding?.remediation && (
        <div className="mt-3 rounded-lg border border-sky-500/10 bg-sky-500/[0.04] p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-sky-300">Remediation</p>
          <p className="mt-1 whitespace-pre-wrap break-words text-sm leading-6 text-slate-300">{finding.remediation}</p>
        </div>
      )}
    </article>
  );
}

export default FindingCard;
