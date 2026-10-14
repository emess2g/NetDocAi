import { Link } from "react-router-dom";
import {
  ArrowLeft,
  FileSearch,
  Plus,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react";
import ReportDashboard from "./ReportDashboard";

function Dashboard() {
  const storedAnalysis = sessionStorage.getItem("netdoc:lastAnalysis");

  let network = null;

  if (storedAnalysis) {
    try {
      network = JSON.parse(storedAnalysis);
    } catch (error) {
      console.error("Could not read stored analysis:", error);
    }
  }

  if (!network) {
    return (
      <div className="px-5 py-16 sm:px-6 md:py-24">
        <div className="mx-auto max-w-3xl text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-slate-500">
            <FileSearch size={24} />
          </div>

          <p className="mt-6 text-xs font-semibold uppercase tracking-widest text-blue-400">
            Dashboard
          </p>

          <h1 className="mt-3 text-3xl font-bold text-white">
            No analysis yet
          </h1>

          <p className="mx-auto mt-4 max-w-xl text-sm leading-6 text-slate-500">
            Analyze a Cisco configuration first. Your latest analysis will
            appear here with the complete network report.
          </p>

          <Link
            to="/analyze"
            className="mt-7 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
          >
            <Plus size={16} />
            Analyze configuration
          </Link>
        </div>
      </div>
    );
  }

  /*
   * ---------------------------------------------------------
   * HEALTH NORMALIZATION
   * ---------------------------------------------------------
   *
   * Backend may return:
   *
   * health: {
   *   score: 90,
   *   status: "Excellent"
   * }
   *
   * Or an older format:
   *
   * health_score: 90
   *
   * This converts both formats into safe display values.
   */

  const healthScore =
    typeof network.health === "object" && network.health !== null
      ? network.health.score
      : (network.health_score ?? network.health ?? null);

  const healthStatus =
    typeof network.health === "object" && network.health !== null
      ? network.health.status
      : null;

  /*
   * ---------------------------------------------------------
   * FINDINGS
   * ---------------------------------------------------------
   */

  const findings = Array.isArray(network.findings) ? network.findings : [];

  const critical = findings.filter(
    (finding) => String(finding?.severity || "").toLowerCase() === "critical",
  ).length;

  const high = findings.filter(
    (finding) => String(finding?.severity || "").toLowerCase() === "high",
  ).length;

  const medium = findings.filter(
    (finding) => String(finding?.severity || "").toLowerCase() === "medium",
  ).length;

  return (
    <div className="px-5 py-10 sm:px-6 md:py-14">
      <div className="mx-auto max-w-7xl">
        {/* HEADER */}
        <div className="mb-8 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <Link
              to="/analyze"
              className="inline-flex items-center gap-2 text-xs font-medium text-slate-500 transition hover:text-white"
            >
              <ArrowLeft size={14} />
              Analyze another configuration
            </Link>

            <div className="mt-6">
              <p className="text-xs font-semibold uppercase tracking-widest text-blue-400">
                Network Analysis
              </p>

              <h1 className="mt-2 text-3xl font-bold text-white">
                {network.hostname || "Unknown Device"}
              </h1>

              <p className="mt-2 text-sm text-slate-500">
                Configuration analysis and network intelligence report
              </p>
            </div>
          </div>

          {/* STATUS SUMMARY */}
          <div className="flex flex-wrap gap-2">
            {/* HEALTH */}
            <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2">
              <CheckCircle2 size={14} className="text-green-400" />

              <span className="text-xs text-slate-400">Health</span>

              <span className="text-sm font-semibold text-white">
                {healthScore ?? "—"}
              </span>

              {healthStatus && (
                <span className="text-xs text-slate-500">{healthStatus}</span>
              )}
            </div>

            {/* CRITICAL */}
            {critical > 0 && (
              <div className="flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-2">
                <AlertTriangle size={14} className="text-red-400" />

                <span className="text-xs text-red-400">
                  {critical} Critical
                </span>
              </div>
            )}

            {/* HIGH */}
            {high > 0 && (
              <div className="rounded-lg border border-orange-500/20 bg-orange-500/5 px-3 py-2 text-xs text-orange-400">
                {high} High
              </div>
            )}

            {/* MEDIUM */}
            {medium > 0 && (
              <div className="rounded-lg border border-yellow-500/20 bg-yellow-500/5 px-3 py-2 text-xs text-yellow-400">
                {medium} Medium
              </div>
            )}
          </div>
        </div>

        {/* ACTUAL REPORT */}
        <ReportDashboard network={network} />
      </div>
    </div>
  );
}

export default Dashboard;
