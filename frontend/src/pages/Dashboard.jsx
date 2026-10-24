import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  FileSearch,
  Plus,
  AlertTriangle,
  CheckCircle2,
  Download,
} from "lucide-react";

import { exportNetworkReport } from "../utils/exportNetworkReport";
import { supabase } from "../lib/supabase";
import ReportDashboard from "./ReportDashboard";

function Dashboard() {
  const { analysisId } = useParams();

  const [savedAnalysis, setSavedAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState("");

  function handleExportPDF() {
    try {
      setExportError("");
      setExporting(true);

      exportNetworkReport(network, {
        hostname: savedAnalysis?.hostname,
        createdAt: savedAnalysis?.created_at,
      });
    } catch (err) {
      setExportError(err.message || "Could not export the PDF report.");
    } finally {
      setExporting(false);
    }
  }

  useEffect(() => {
    let cancelled = false;

    async function loadAnalysis() {
      setLoading(true);
      setError("");
      setSavedAnalysis(null);

      try {
        const {
          data: { user },
          error: userError,
        } = await supabase.auth.getUser();

        if (userError || !user) {
          throw new Error("Please sign in to view your analyses.");
        }

        let query = supabase
          .from("analyses")
          .select(
            "id, hostname, health_score, health_status, analysis, config_text, source_filename, created_at",
          );

        if (analysisId) {
          query = query.eq("id", analysisId);
        } else {
          query = query.order("created_at", { ascending: false }).limit(1);
        }

        const { data, error: queryError } = await query.maybeSingle();

        if (queryError) {
          throw new Error("Could not load the requested analysis.");
        }

        if (!cancelled) {
          setSavedAnalysis(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Could not load your analysis.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadAnalysis();

    return () => {
      cancelled = true;
    };
  }, [analysisId]);

  const network = savedAnalysis?.analysis ?? null;

  if (loading) {
    return (
      <div className="px-5 py-12 sm:px-6 md:py-16" role="status" aria-live="polite">
        <div className="mx-auto max-w-7xl">
          <div className="mb-8 border-b border-white/10 pb-6">
            <div className="h-3 w-32 animate-pulse rounded bg-white/10" />
            <div className="mt-4 h-8 w-64 max-w-full animate-pulse rounded-lg bg-white/10" />
            <div className="mt-3 h-4 w-48 max-w-full animate-pulse rounded bg-white/5" />
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[0, 1, 2, 3].map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-[#0d131d] p-5">
                <div className="h-3 w-24 animate-pulse rounded bg-white/10" />
                <div className="mt-4 h-8 w-16 animate-pulse rounded bg-white/10" />
                <div className="mt-3 h-3 w-32 animate-pulse rounded bg-white/5" />
              </div>
            ))}
          </div>
          <p className="mt-6 text-center text-xs text-slate-500">Loading your saved analysis…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-5 py-16 sm:px-6 md:py-24">
        <div className="mx-auto max-w-2xl rounded-2xl border border-red-400/15 bg-[#0d131d] p-8 text-center sm:p-10">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl border border-red-400/20 bg-red-400/5 text-red-300">
            <AlertTriangle size={22} />
          </div>
          <p className="mt-5 text-lg font-semibold text-white">We couldn’t load this report</p>
          <p className="mt-2 text-sm leading-6 text-slate-400" role="alert">{error}</p>

        <button
          type="button"
          onClick={() => window.location.reload()}
          className="mt-6 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-300"
        >
          Try again
        </button>

        <div>
          <Link
            to="/history"
            className="mt-4 inline-block text-sm text-slate-400 hover:text-white"
          >
            Return to analysis history
          </Link>
        </div>
      </div>
    );
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
            {analysisId ? "Analysis not found" : "No analysis yet"}
          </h1>

          <p className="mx-auto mt-4 max-w-xl text-sm leading-6 text-slate-500">
            {analysisId
              ? "This report may not exist or may not be accessible to your account."
              : "Analyze a Cisco configuration first. Your latest saved report will appear here."}
          </p>

          <div className="mt-7 flex flex-wrap justify-center gap-3">
            <Link
              to="/analyze"
              className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
            >
              <Plus size={16} />
              Analyze configuration
            </Link>

            <Link
              to="/history"
              className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-5 py-3 text-sm font-semibold text-slate-300 transition hover:bg-white/5 hover:text-white"
            >
              <FileSearch size={16} />
              Analysis history
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const healthScore =
    typeof network.health === "object" && network.health !== null
      ? (network.health.score ?? savedAnalysis.health_score ?? null)
      : (savedAnalysis.health_score ?? network.health ?? null);

  const healthStatus =
    typeof network.health === "object" && network.health !== null
      ? (network.health.status ?? savedAnalysis.health_status ?? null)
      : (savedAnalysis.health_status ?? null);

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
        <div className="mb-8">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0">
              <p className="text-xs font-medium tracking-wide text-slate-500">
                {network.report_type === "syslog" ? "SYSLOG EVENT REPORT" : "NETWORK REPORT"}
              </p>

              <h1 className="mt-2 break-words text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                {savedAnalysis.hostname || network.hostname || "Unknown Device"}
              </h1>

              <p className="mt-2 text-sm text-slate-400">
                {savedAnalysis.created_at
                  ? new Date(savedAnalysis.created_at).toLocaleString()
                  : "Saved analysis"}
                {savedAnalysis.source_filename
                  ? ` · ${savedAnalysis.source_filename}`
                  : ""}
              </p>
            </div>

            <button
              type="button"
              onClick={handleExportPDF}
              disabled={exporting}
              aria-busy={exporting}
              className="inline-flex shrink-0 items-center justify-center gap-2 self-start rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-300 focus-visible:ring-offset-2 focus-visible:ring-offset-[#070b12] disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Download size={16} />
              {exporting ? "Preparing..." : "Export PDF"}
            </button>
          </div>

          {exportError && (
            <p className="mt-3 text-sm text-red-400" role="alert">
              {exportError}
            </p>
          )}

          <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-3 border-y border-white/10 py-4">
            <div>
              <span className="text-xs text-slate-500">Health score</span>
              <p className="mt-1 text-sm font-semibold text-white">
                {healthScore ?? "—"}
                {healthStatus && (
                  <span className="ml-2 text-xs font-normal text-slate-400">
                    {healthStatus}
                  </span>
                )}
              </p>
            </div>

            <div>
              <span className="text-xs text-slate-500">Findings</span>
              <p className="mt-1 text-sm font-semibold text-white">
                {findings.length}
              </p>
            </div>

            {critical > 0 && (
              <div>
                <span className="text-xs text-slate-500">Critical</span>
                <p className="mt-1 text-sm font-semibold text-red-400">
                  {critical}
                </p>
              </div>
            )}

            {high > 0 && (
              <div>
                <span className="text-xs text-slate-500">High</span>
                <p className="mt-1 text-sm font-semibold text-orange-400">
                  {high}
                </p>
              </div>
            )}

            {medium > 0 && (
              <div>
                <span className="text-xs text-slate-500">Medium</span>
                <p className="mt-1 text-sm font-semibold text-yellow-400">
                  {medium}
                </p>
              </div>
            )}
          </div>

          <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2">
            {savedAnalysis.config_text && (
              <Link
                to="/analyze"
                state={{
                  config: savedAnalysis.config_text,
                  fileName: savedAnalysis.source_filename || "",
                }}
                className="text-xs text-slate-400 transition hover:text-white"
              >
                Edit configuration
              </Link>
            )}

            <Link
              to="/analyze"
              className="text-xs text-slate-400 transition hover:text-white"
            >
              Analyze another
            </Link>

            <Link
              to="/history"
              className="text-xs text-slate-400 transition hover:text-white"
            >
              View history
            </Link>
          </div>
        </div>

        <ReportDashboard network={network} />
      </div>
    </div>
  );
}

export default Dashboard;
