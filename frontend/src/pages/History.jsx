import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft,
  FileSearch,
  Clock3,
  Network,
  RefreshCw,
  Search,
} from "lucide-react";
import { supabase } from "../lib/supabase";

function formatDate(value) {
  if (!value) return "Date unavailable";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "Date unavailable";

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function History() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  async function loadHistory() {
    setLoading(true);
    setError("");

    try {
      const {
        data: { user },
        error: userError,
      } = await supabase.auth.getUser();

      if (userError || !user) {
        throw new Error("Please sign in to view your analysis history.");
      }

      const { data, error: queryError } = await supabase
        .from("analyses")
        .select(
          "id, user_id, hostname, health_score, health_status, analysis, config_text, source_filename, created_at",
        )
        .order("created_at", { ascending: false });

      if (queryError) {
        throw new Error("Could not load your analysis history.");
      }

      setAnalyses(data ?? []);
    } catch (err) {
      setError(err.message || "Something went wrong loading your history.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  const filteredAnalyses = analyses.filter((item) => {
    const hostname =
      item.hostname || item.analysis?.hostname || "Unknown Device";
    const filename = item.source_filename || "";

    const query = search.trim().toLowerCase();

    return (
      !query ||
      hostname.toLowerCase().includes(query) ||
      filename.toLowerCase().includes(query)
    );
  });

  return (
    <main className="min-h-screen px-5 py-10 sm:px-6 md:py-14">
      <div className="mx-auto max-w-6xl">
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 text-xs font-medium text-slate-500 transition hover:text-white"
        >
          <ArrowLeft size={14} />
          Back to dashboard
        </Link>

        <div className="mt-8 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-blue-400">
              Your workspace
            </p>
            <h1 className="mt-2 text-3xl font-bold text-white">
              Analysis History
            </h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-400">
              Browse previous network reports and reopen an analysis whenever
              you need it.
            </p>
          </div>

          <Link
            to="/analyze"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
          >
            <Network size={16} />
            New analysis
          </Link>
        </div>

        <div className="mt-8 flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-4">
          <Search size={17} className="shrink-0 text-slate-500" />
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by hostname or filename..."
            className="w-full bg-transparent py-4 text-sm text-white outline-none placeholder:text-slate-600"
          />
        </div>

        {loading ? (
          <div className="py-20 text-center text-sm text-slate-400">
            Loading your analysis history...
          </div>
        ) : error ? (
          <div className="mt-8 rounded-xl border border-red-500/20 bg-red-500/5 p-6">
            <p className="text-sm text-red-400">{error}</p>
            <button
              type="button"
              onClick={loadHistory}
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-white/5 px-4 py-2 text-sm text-white hover:bg-white/10"
            >
              <RefreshCw size={14} />
              Try again
            </button>
          </div>
        ) : filteredAnalyses.length === 0 ? (
          <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.02] px-6 py-16 text-center">
            <FileSearch size={28} className="mx-auto text-slate-500" />
            <h2 className="mt-5 text-lg font-semibold text-white">
              {analyses.length
                ? "No matching analyses"
                : "No saved analyses yet"}
            </h2>
            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
              {analyses.length
                ? "Try another hostname or filename."
                : "Your completed analyses will appear here after they have been saved."}
            </p>
            {!analyses.length && (
              <Link
                to="/analyze"
                className="mt-6 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white hover:bg-blue-500"
              >
                <Network size={16} />
                Analyze configuration
              </Link>
            )}
          </div>
        ) : (
          <div className="mt-6 overflow-hidden rounded-2xl border border-white/10 bg-white/[0.02]">
            <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
              <span className="text-sm font-medium text-white">
                Saved analyses
              </span>
              <span className="text-xs text-slate-500">
                {filteredAnalyses.length}{" "}
                {filteredAnalyses.length === 1 ? "record" : "records"}
              </span>
            </div>

            <div className="divide-y divide-white/5">
              {filteredAnalyses.map((item) => {
                const hostname =
                  item.hostname || item.analysis?.hostname || "Unknown Device";

                const health =
                  item.health_score ??
                  (typeof item.analysis?.health === "object"
                    ? item.analysis.health?.score
                    : item.analysis?.health);

                return (
                  <article
                    key={item.id}
                    className="flex flex-col gap-4 px-5 py-5 transition hover:bg-white/[0.025] sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div className="min-w-0">
                      <h2 className="truncate text-sm font-semibold text-white">
                        {hostname}
                      </h2>

                      <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-500">
                        <span className="inline-flex items-center gap-1.5">
                          <Clock3 size={13} />
                          {formatDate(item.created_at)}
                        </span>

                        {item.source_filename && (
                          <span className="max-w-full truncate">
                            File: {item.source_filename}
                          </span>
                        )}

                        {health !== null && health !== undefined && (
                          <span>Health: {health}/100</span>
                        )}
                      </div>
                    </div>

                    <Link
                      to={`/dashboard/${item.id}`}
                      className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg border border-blue-500/20 bg-blue-500/10 px-4 py-2.5 text-xs font-semibold text-blue-300 transition hover:bg-blue-500/20"
                    >
                      <FileSearch size={14} />
                      Open report
                    </Link>
                  </article>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

export default History;
