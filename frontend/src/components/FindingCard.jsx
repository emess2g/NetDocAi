function asText(value) {
  if (typeof value === "string") return value;
  if (typeof value === "number") return String(value);
  return "";
}

function asList(value) {
  if (Array.isArray(value)) {
    return value
      .map((item) =>
        typeof item === "string"
          ? item
          : item?.description || item?.action || item?.message || "",
      )
      .filter(Boolean);
  }

  return typeof value === "string" && value.trim() ? [value] : [];
}

function FindingCard({ finding }) {
  const severity = String(finding?.severity || "info").toLowerCase();
  const severityStyles = {
    critical: {
      badge: "border-red-400/20 bg-red-400/10 text-red-300",
      dot: "bg-red-400",
      rail: "bg-red-400",
    },
    high: {
      badge: "border-orange-400/20 bg-orange-400/10 text-orange-300",
      dot: "bg-orange-400",
      rail: "bg-orange-400",
    },
    medium: {
      badge: "border-amber-300/20 bg-amber-300/10 text-amber-200",
      dot: "bg-amber-300",
      rail: "bg-amber-300",
    },
    warning: {
      badge: "border-amber-300/20 bg-amber-300/10 text-amber-200",
      dot: "bg-amber-300",
      rail: "bg-amber-300",
    },
    low: {
      badge: "border-blue-400/20 bg-blue-400/10 text-blue-300",
      dot: "bg-blue-400",
      rail: "bg-blue-400",
    },
    info: {
      badge: "border-slate-400/20 bg-slate-400/10 text-slate-300",
      dot: "bg-slate-400",
      rail: "bg-slate-400",
    },
  };
  const style = severityStyles[severity] || severityStyles.info;
  const evidence = asList(finding?.evidence);
  const remediationSteps = asList(finding?.remediation_steps);
  const verificationSteps = asList(finding?.verification_steps);
  const references = asList(finding?.references);
  const title =
    asText(finding?.title) ||
    asText(finding?.finding) ||
    asText(finding?.message) ||
    "Unspecified finding";
  const impact =
    asText(finding?.potential_impact) ||
    asText(finding?.impact) ||
    asText(finding?.why_it_matters);
  const recommendation =
    asText(finding?.recommendation) ||
    asText(finding?.remediation);

  return (
    <article className="group relative overflow-hidden rounded-2xl border border-white/[0.09] bg-[#0d131d] transition-colors duration-200 hover:border-white/[0.16]">
      <div className={"absolute inset-y-0 left-0 w-[3px] " + style.rail} />

      <div className="p-5 pl-6 sm:p-6 sm:pl-7">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex min-w-0 flex-wrap items-center gap-2">
            <span
              className={
                "inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.12em] " +
                style.badge
              }
            >
              <span className={"h-1.5 w-1.5 rounded-full " + style.dot} />
              {severity}
            </span>

            {finding?.category && (
              <span className="rounded-full border border-white/[0.08] bg-white/[0.03] px-2.5 py-1 text-[10px] font-medium uppercase tracking-[0.1em] text-slate-400">
                {finding.category}
              </span>
            )}

            {finding?.rule_id && (
              <span className="font-mono text-[10px] text-slate-600">
                {finding.rule_id}
              </span>
            )}
          </div>

          {finding?.confidence && (
            <span className="shrink-0 text-[11px] text-slate-500">
              Confidence{" "}
              <strong className="font-semibold text-slate-300">
                {finding.confidence}
              </strong>
            </span>
          )}
        </div>

        <h3 className="mt-4 text-[15px] font-semibold leading-6 tracking-[-0.01em] text-slate-100 sm:text-base">
          {title}
        </h3>

        {(finding?.device || finding?.timestamp || finding?.event_code) && (
          <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-slate-500">
            {finding?.device && (
              <span>
                Device{" "}
                <strong className="font-medium text-slate-300">
                  {finding.device}
                </strong>
              </span>
            )}
            {finding?.timestamp && (
              <time dateTime={finding.timestamp}>{finding.timestamp}</time>
            )}
            {finding?.event_code && (
              <span className="font-mono text-slate-400">
                {finding.event_code}
              </span>
            )}
          </div>
        )}

        {impact && (
          <section className="mt-4 rounded-xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-500">
              Why this matters
            </p>
            <p className="mt-2 break-words text-sm leading-6 text-slate-300">
              {impact}
            </p>
          </section>
        )}

        {evidence.length > 0 && (
          <section className="mt-3 overflow-hidden rounded-xl border border-white/[0.07] bg-[#080d15]">
            <div className="flex items-center justify-between border-b border-white/[0.06] px-4 py-3">
              <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-500">
                Evidence from input
              </p>
              <span className="text-[10px] text-slate-600">
                {evidence.length} item{evidence.length === 1 ? "" : "s"}
              </span>
            </div>
            <div className="space-y-2 p-4">
              {evidence.map((item, index) => (
                <pre
                  key={index}
                  className="overflow-x-auto whitespace-pre-wrap break-words font-mono text-xs leading-5 text-cyan-100/75"
                >
                  {item}
                </pre>
              ))}
            </div>
          </section>
        )}

        {(recommendation || remediationSteps.length > 0) && (
          <section className="mt-3 rounded-xl border border-blue-400/15 bg-blue-400/[0.045] p-4">
            <div className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
              <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-200/80">
                Recommended action
              </p>
            </div>
            {recommendation && (
              <p className="mt-2 text-sm leading-6 text-slate-300">
                {recommendation}
              </p>
            )}
            {remediationSteps.length > 0 && (
              <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm leading-6 text-slate-300 marker:text-blue-300">
                {remediationSteps.map((step, index) => (
                  <li key={index}>{step}</li>
                ))}
              </ol>
            )}
          </section>
        )}

        {verificationSteps.length > 0 && (
          <section className="mt-3 rounded-xl border border-emerald-400/15 bg-emerald-400/[0.035] p-4">
            <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-emerald-200/80">
              Verify the change
            </p>
            <ul className="mt-2 list-disc space-y-1.5 pl-5 text-sm leading-6 text-slate-300 marker:text-emerald-300">
              {verificationSteps.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ul>
          </section>
        )}

        {references.length > 0 && (
          <div className="mt-4 border-t border-white/[0.06] pt-3">
            <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-600">
              References
            </p>
            <ul className="mt-2 space-y-1 text-xs text-slate-400">
              {references.map((reference, index) => (
                <li key={index} className="break-words">
                  {reference}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </article>
  );
}

export default FindingCard;
