import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  CircleAlert,
  Clock3,
  FileSearch,
  Network,
  Plus,
  ShieldAlert,
} from "lucide-react";
import { supabase } from "../lib/supabase";

const panel = "rounded-xl border border-[#243040] bg-[#101723]";
const muted = "text-[#8596b0]";

function getHealth(analysis) {
  const report = analysis?.analysis ?? {};
  const health = report.health;
  const score =
    analysis?.health_score ??
    (typeof health === "object" && health !== null ? health.score : health);
  const status =
    analysis?.health_status ??
    (typeof health === "object" && health !== null ? health.status : null);
  return {
    score: score !== null && score !== undefined && score !== "" && Number.isFinite(Number(score)) ? Number(score) : null,
    status: status || "Not scored",
  };
}

function getFindings(analysis) {
  return Array.isArray(analysis?.analysis?.findings)
    ? analysis.analysis.findings
    : [];
}

function formatFindingValue(value) {
  if (value === null || value === undefined || value === "") return "";
  if (typeof value === "string" || typeof value === "number") return String(value);
  if (Array.isArray(value)) {
    return value.map(formatFindingValue).filter(Boolean).join(" · ");
  }
  if (typeof value === "object") {
    return Object.entries(value)
      .map(([key, item]) => {
        const formatted = formatFindingValue(item);
        return formatted ? `${key}: ${formatted}` : "";
      })
      .filter(Boolean)
      .join("; ");
  }
  return "";
}

function DashboardOverview() {
  const [analyses, setAnalyses] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadOverview() {
    setLoading(true);
    setError("");
    try {
      const { data, error: queryError, count } = await supabase
        .from("analyses")
        .select("id, hostname, health_score, health_status, analysis, source_filename, created_at", { count: "exact" })
        .order("created_at", { ascending: false })
        .limit(50);

      if (queryError) throw queryError;
      setAnalyses(Array.isArray(data) ? data : []);
      setTotalCount(count ?? data?.length ?? 0);
    } catch (err) {
      setError(err?.message || "Could not load your dashboard.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadOverview();
  }, []);

  const stats = useMemo(() => {
    const findings = analyses.flatMap(getFindings);
    const critical = findings.filter((item) => String(item?.severity || "").toLowerCase() === "critical").length;
    const high = findings.filter((item) => String(item?.severity || "").toLowerCase() === "high").length;
    const healthy = analyses.filter((item) => {
      const health = getHealth(item);
      const status = health.status.toLowerCase();
      return status === "excellent" || status === "good" || (health.score !== null && health.score >= 80);
    }).length;
    return { findings, critical, high, healthy };
  }, [analyses]);

  const latest = analyses[0] ?? null;
  const latestHealth = latest ? getHealth(latest) : { score: null, status: "No report yet" };
  const latestNetwork = latest?.analysis ?? {};
  const interfaces = Array.isArray(latestNetwork.interfaces) ? latestNetwork.interfaces : [];
  const vlans = Array.isArray(latestNetwork.vlans) ? latestNetwork.vlans : [];
  const latestFindings = latest ? getFindings(latest) : [];
  const severityRows = [
    { label: "Critical", key: "critical", color: "#fa5963", count: stats.critical },
    { label: "High", key: "high", color: "#faad40", count: stats.high },
    { label: "Medium", key: "medium", color: "#f4d35e", count: stats.findings.filter((f) => String(f?.severity || "").toLowerCase() === "medium").length },
    { label: "Low", key: "low", color: "#3dd4e3", count: stats.findings.filter((f) => String(f?.severity || "").toLowerCase() === "low").length },
  ];
  const maxSeverity = Math.max(1, ...severityRows.map((item) => item.count));

  return (
    <div className="min-w-0 flex-1 px-4 py-7 sm:px-6 lg:px-8 lg:py-9">
      <div className="mx-auto max-w-[1440px]">
        <div className="mb-7 flex flex-col gap-4 border-b border-[#243040] pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className={"text-[10px] font-semibold uppercase tracking-[0.18em] " + muted}>Workspace / Overview</p>
            <h1 className="mt-3 text-2xl font-bold tracking-tight text-[#e8f0fa] sm:text-[30px]">Network overview</h1>
            <p className={"mt-2 text-sm " + muted}>Understand your network configuration at a glance.</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden rounded-lg bg-[#142438] px-3 py-2 text-[10px] font-bold tracking-wide text-[#3dd4e3] sm:inline-flex">CONFIG ANALYSIS</span>
            <Link to="/analyze" className="inline-flex items-center gap-2 rounded-lg bg-[#4585fa] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3dd4e3]">
              <Plus size={16} /> Analyze
            </Link>
          </div>
        </div>

        {error && (
          <div role="alert" className="mb-6 flex flex-col gap-3 rounded-xl border border-red-400/20 bg-red-400/5 p-4 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-red-200">{error}</p>
            <button onClick={loadOverview} className="rounded-lg border border-red-300/20 px-3 py-2 text-sm text-red-100 hover:bg-red-400/10">Try again</button>
          </div>
        )}

        <section aria-label="Workspace metrics" className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {[
            { label: "Configurations analyzed", value: loading ? "—" : totalCount, note: "Saved reports in your workspace", color: "#4585fa", icon: Activity },
            { label: "Healthy configurations", value: loading ? "—" : stats.healthy, note: "Good or excellent in latest 50", color: "#38c791", icon: CheckCircle2 },
            { label: "Open findings", value: loading ? "—" : stats.findings.length, note: "Across latest 50 saved reports", color: "#faad40", icon: CircleAlert },
            { label: "High-risk findings", value: loading ? "—" : stats.critical + stats.high, note: "Critical and high severity", color: "#fa5963", icon: ShieldAlert },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <article key={item.label} className={panel + " relative overflow-hidden p-4 sm:p-5"}>
                <span className="absolute inset-y-0 left-0 w-[3px]" style={{ backgroundColor: item.color }} />
                <div className="flex items-start justify-between gap-3">
                  <p className={"text-xs font-medium " + muted}>{item.label}</p>
                  <span className="rounded-lg p-2" style={{ backgroundColor: item.color + "18", color: item.color }}><Icon size={16} /></span>
                </div>
                <p className="mt-3 text-3xl font-bold tracking-tight text-[#e8f0fa]">{item.value}</p>
                <p className="mt-2 text-[11px]" style={{ color: item.color }}>{item.note}</p>
              </article>
            );
          })}
        </section>

        <div className="mt-5 grid gap-4 xl:grid-cols-[minmax(300px,0.95fr)_minmax(0,1.8fr)]">
          <section className={panel + " p-5 sm:p-6"}>
            <p className={"text-[10px] font-bold tracking-[0.16em] " + muted}>NETWORK HEALTH</p>
            <h2 className="mt-3 text-lg font-semibold text-[#e8f0fa]">{latest ? latestHealth.status : "Your overview starts here"}</h2>
            <p className={"mt-1 text-xs " + muted}>{latest ? "Based on the most recently saved report" : "Analyze a configuration to see its health score."}</p>
            <div className="mt-7 flex flex-col items-center gap-5 sm:flex-row sm:justify-center sm:gap-7">
              <div className="relative flex h-32 w-32 shrink-0 items-center justify-center rounded-full" style={{ background: latestHealth.score === null ? "#172333" : "conic-gradient(#38c791 " + (Math.max(0, Math.min(100, latestHealth.score)) * 1) + "%, #243040 0)" }}>
                <div className="flex h-[104px] w-[104px] flex-col items-center justify-center rounded-full border border-[#243040] bg-[#101723]">
                  <span className="text-3xl font-bold text-[#e8f0fa]">{latestHealth.score ?? "—"}</span>
                  <span className={"text-[10px] " + muted}>/ 100</span>
                </div>
              </div>
              <div className="max-w-xs">
                <span className="inline-flex rounded-md bg-[#123329] px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-[#38c791]">{latest ? latestHealth.status : "Awaiting data"}</span>
                <p className="mt-3 text-sm font-medium text-[#e8f0fa]">{latest ? (latestFindings.length ? latestFindings.length + " finding(s) detected." : "No findings recorded in this report.") : "No critical assumptions. Your real report data will appear here."}</p>
                <p className={"mt-2 text-xs leading-5 " + muted}>{latest ? "Review the evidence before changing device configurations." : "Your dashboard uses saved analysis data; sample numbers are never substituted."}</p>
              </div>
            </div>
            <div className="mt-7 flex items-center justify-between border-t border-[#243040] pt-4 text-xs">
              <span className={muted}>Latest report</span>
              {latest ? <Link to={"/dashboard/" + latest.id} className="inline-flex items-center gap-1 font-semibold text-[#3dd4e3] hover:text-white">Open report <ArrowUpRight size={13} /></Link> : <Link to="/analyze" className="font-semibold text-[#3dd4e3] hover:text-white">Start analysis <ArrowUpRight size={13} /></Link>}
            </div>
          </section>

          <section className={panel + " p-5 sm:p-6"}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-base font-semibold text-[#e8f0fa]">Findings by severity</h2>
                <p className={"mt-1 text-xs " + muted}>Severity totals across the latest 50 saved reports</p>
              </div>
              <Link to="/history" className="shrink-0 rounded-lg border border-[#243040] px-3 py-2 text-[11px] font-semibold text-[#b7c5d9] hover:bg-white/5">View history</Link>
            </div>
            <div className="mt-7 space-y-5">
              {severityRows.map((item) => (
                <div key={item.key} className="grid grid-cols-[68px_minmax(0,1fr)_32px] items-center gap-3 sm:grid-cols-[86px_minmax(0,1fr)_36px]">
                  <span className="text-xs text-[#c7d3e3]">{item.label}</span>
                  <div className="h-2 overflow-hidden rounded-full bg-[#243040]">
                    <div className="h-full rounded-full transition-all" style={{ width: ((item.count / maxSeverity) * 100) + "%", backgroundColor: item.color }} />
                  </div>
                  <span className="text-right text-xs font-semibold tabular-nums text-[#e8f0fa]">{loading ? "—" : item.count}</span>
                </div>
              ))}
            </div>
            <p className={"mt-7 border-t border-[#243040] pt-4 text-xs leading-5 " + muted}>Finding counts are calculated from saved reports. The same issue may appear in more than one report.</p>
          </section>
        </div>

        <div className="mt-5 grid gap-4 xl:grid-cols-2">
          <section className={panel + " overflow-hidden"}>
            <div className="flex items-start justify-between gap-4 p-5 sm:p-6">
              <div>
                <h2 className="text-base font-semibold text-[#e8f0fa]">Network snapshot</h2>
                <p className={"mt-1 text-xs " + muted}>Interface and VLAN data from the latest report</p>
              </div>
              <span className="rounded-md bg-[#142438] px-2.5 py-1 text-[10px] font-semibold text-[#3dd4e3]">LATEST REPORT</span>
            </div>
            {!latest ? (
              <div className={"border-t border-[#243040] px-5 py-10 text-center text-sm " + muted}><Network size={24} className="mx-auto mb-3 opacity-70" />No saved configuration yet.<Link to="/analyze" className="ml-1 text-[#3dd4e3] hover:text-white">Analyze one</Link></div>
            ) : (
              <div className="grid grid-cols-2 gap-3 border-t border-[#243040] p-5">
                <div className="rounded-lg bg-[#0c111b] p-4"><p className={"text-xs " + muted}>Interfaces</p><p className="mt-2 text-2xl font-bold text-[#e8f0fa]">{interfaces.length}</p></div>
                <div className="rounded-lg bg-[#0c111b] p-4"><p className={"text-xs " + muted}>VLANs</p><p className="mt-2 text-2xl font-bold text-[#e8f0fa]">{vlans.length}</p></div>
                <div className="col-span-2 divide-y divide-[#243040]">
                  {interfaces.slice(0, 4).map((item, index) => (
                    <div key={(item.name || item.interface || "interface") + index} className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto] items-center gap-3 py-3 text-xs">
                      <span className="truncate font-medium text-[#e8f0fa]">{item.name || item.interface || "Interface"}</span>
                      <span className={"truncate " + muted}>{item.ip_address || item.ip || "No IP assigned"}</span>
                      <span className={String(item.status || "").toLowerCase().includes("up") ? "text-[#38c791]" : "text-[#8596b0]"}>{item.status || "Unknown"}</span>
                    </div>
                  ))}
                </div>
                <Link to={"/dashboard/" + latest.id} className="col-span-2 inline-flex items-center gap-2 text-xs font-semibold text-[#3dd4e3] hover:text-white">Open full network report <ArrowUpRight size={14} /></Link>
              </div>
            )}
          </section>

          <section className={panel + " overflow-hidden"}>
            <div className="flex items-start justify-between gap-4 p-5 sm:p-6">
              <div>
                <h2 className="text-base font-semibold text-[#e8f0fa]">Priority findings</h2>
                <p className={"mt-1 text-xs " + muted}>Highest-severity findings from the latest report</p>
              </div>
              <span className="rounded-md bg-[#142438] px-2.5 py-1 text-[10px] font-semibold text-[#3dd4e3]">{latestFindings.length} TOTAL</span>
            </div>
            {!latest ? (
              <div className={"border-t border-[#243040] px-5 py-10 text-center text-sm " + muted}><AlertTriangle size={24} className="mx-auto mb-3 opacity-70" />Priority findings appear after analysis.</div>
            ) : latestFindings.length === 0 ? (
              <div className={"border-t border-[#243040] px-5 py-10 text-center text-sm " + muted}><CheckCircle2 size={22} className="mx-auto mb-3 text-[#38c791]" />No findings in the latest report.</div>
            ) : (
              <div className="divide-y divide-[#243040] border-t border-[#243040]">
                {latestFindings.slice(0, 4).map((finding, index) => {
                  const severity = String(finding?.severity || "info").toLowerCase();
                  const color = severity === "critical" ? "#fa5963" : severity === "high" ? "#faad40" : severity === "medium" ? "#f4d35e" : "#3dd4e3";
                  return <div key={finding.id || finding.title || index} className="flex items-start gap-3 px-5 py-4">
                    <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full" style={{ backgroundColor: color }} />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-[#e8f0fa]">{finding.title || finding.name || "Configuration finding"}</p>
                      <p className={"mt-1 line-clamp-2 text-xs leading-5 " + muted}>{formatFindingValue(finding.evidence || finding.description || finding.message) || "Review the full report for supporting details."}</p>
                    </div>
                    <span className="shrink-0 rounded-md px-2 py-1 text-[9px] font-bold uppercase" style={{ color, backgroundColor: color + "18" }}>{severity}</span>
                  </div>;
                })}
                <div className="px-5 py-3"><Link to={"/dashboard/" + latest.id} className="inline-flex items-center gap-1 text-xs font-semibold text-[#3dd4e3] hover:text-white">View report <ArrowUpRight size={13} /></Link></div>
              </div>
            )}
          </section>
        </div>

        <section className={panel + " mt-5 overflow-hidden"}>
          <div className="flex items-center justify-between gap-4 p-5 sm:p-6">
            <div><h2 className="text-base font-semibold text-[#e8f0fa]">Recent report activity</h2><p className={"mt-1 text-xs " + muted}>Your most recent saved analyses</p></div>
            <Link to="/history" className="inline-flex items-center gap-1 text-xs font-semibold text-[#3dd4e3] hover:text-white">All history <ArrowUpRight size={13} /></Link>
          </div>
          {loading ? <div className={"border-t border-[#243040] px-5 py-8 text-sm " + muted}>Loading saved reports…</div> : analyses.length === 0 ? <div className={"border-t border-[#243040] px-5 py-8 text-sm " + muted}>No report activity yet.</div> : (
            <div className="divide-y divide-[#243040] border-t border-[#243040]">
              {analyses.slice(0, 5).map((item) => {
                const health = getHealth(item);
                const hostname = item.hostname || item.analysis?.hostname || "Unknown device";
                return <Link key={item.id} to={"/dashboard/" + item.id} className="flex flex-col gap-2 px-5 py-4 transition hover:bg-white/[0.025] sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex min-w-0 items-start gap-3"><span className="mt-0.5 rounded-lg bg-[#142438] p-2 text-[#3dd4e3]"><Clock3 size={15} /></span><div className="min-w-0"><p className="truncate text-sm font-medium text-[#e8f0fa]">{hostname}</p><p className={"mt-1 truncate text-xs " + muted}>{item.source_filename || "Saved network report"} · {item.created_at ? new Date(item.created_at).toLocaleString() : "Date unavailable"}</p></div></div>
                  <span className="inline-flex items-center gap-1 text-sm font-semibold text-[#e8f0fa]">{health.score ?? "—"}<span className={"text-[10px] font-normal " + muted}>/100</span><ArrowUpRight size={13} className="ml-1 text-[#3dd4e3]" /></span>
                </Link>;
              })}
            </div>
          )}
        </section>

        <p className={"mt-6 text-[10px] " + muted}>Metrics reflect the latest 50 reports where indicated. NetDocAi does not invent device topology or health data.</p>
      </div>
    </div>
  );
}

export default DashboardOverview;
