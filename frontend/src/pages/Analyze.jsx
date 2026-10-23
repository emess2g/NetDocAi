import { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  ArrowLeft,
  FileUp,
  FileText,
  Loader2,
  Network,
  Play,
  X,
} from "lucide-react";
import { supabase } from "../lib/supabase";

function Analyze() {
  const [config, setConfig] = useState("");
  const [fileName, setFileName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const location = useLocation();

  useEffect(() => {
    const savedConfig = location.state?.config;
    const savedFileName = location.state?.fileName;

    setConfig(typeof savedConfig === "string" ? savedConfig : "");
    setFileName(typeof savedConfig === "string" ? savedFileName || "" : "");
    setError("");
  }, [location.key]);

  const analyzeNetwork = async () => {
    if (!config.trim()) {
      setError("Paste a configuration or upload a file first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // 1. Make sure the user is signed in.
      // 1. Get the current Supabase session and access token.
      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession();

      if (sessionError || !session?.access_token || !session.user) {
        setError("Your session has expired. Please sign in again.");
        return;
      }

      const user = session.user;

      // 2. Send the configuration to the existing backend.
      // const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

      // 2. Send the configuration and Supabase access token to FastAPI.
      const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({ config }),
      });

      if (response.status === 401) {
        throw new Error(
          "Your session is invalid or expired. Please sign in again.",
        );
      }

      if (!response.ok) {
        const errorBody = await response.text();

        console.error("Analysis API error:", {
          status: response.status,
          body: errorBody,
        });

        throw new Error(`Analysis failed (${response.status}): ${errorBody}`);
      }

      const data = await response.json();

      // 3. Extract health information safely.
      const healthScore =
        typeof data.health === "object"
          ? (data.health?.score ?? null)
          : (data.health ?? null);

      const healthStatus =
        typeof data.health === "object" ? (data.health?.status ?? null) : null;

      // 4. Save the complete analysis to Supabase.
      const { error: saveError } = await supabase.from("analyses").insert({
        user_id: user.id,
        hostname: data.hostname ?? null,
        health_score: healthScore,
        health_status: healthStatus,
        config_text: config,
        source_filename: fileName || null,
        analysis: data,
      });

      if (saveError) {
        console.error("Supabase save error:", saveError);
        throw new Error("Could not save your analysis.");
      }

      // 5. Keep the latest result available for the current dashboard.
      sessionStorage.setItem("netdoc:lastAnalysis", JSON.stringify(data));

      // 6. Open the dashboard.
      window.location.href = "/dashboard";
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Could not analyze the configuration. Make sure the NetDoc AI backend is running.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleFile = async (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    const allowedExtensions = [".txt", ".cfg", ".conf", ".log"];
    const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();

    if (!allowedExtensions.includes(extension)) {
      setError("Please upload a .txt, .cfg, .conf, or .log file.");
      event.target.value = "";
      return;
    }

    try {
      const text = await file.text();

      setConfig(text);
      setFileName(file.name);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Could not read the selected file.");
    }

    event.target.value = "";
  };

  const clearConfiguration = () => {
    setConfig("");
    setFileName("");
    setError("");
  };

  return (
    <div className="px-5 py-12 sm:px-6 md:py-16">
      <div className="mx-auto max-w-6xl">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-xs font-medium text-slate-500 transition hover:text-white"
        >
          <ArrowLeft size={14} />
          Back to home
        </Link>

        <div className="mt-8 max-w-3xl">
          <div className="flex items-center gap-2 text-blue-400">
            <Network size={17} />

            <span className="text-xs font-semibold uppercase tracking-widest">
              Network & Syslog Analyzer
            </span>
          </div>

          <h1 className="mt-3 text-3xl font-bold text-white sm:text-4xl">
            Analyze a Cisco configuration or Syslog log.
          </h1>

          <p className="mt-4 text-sm leading-6 text-slate-500 sm:text-base">
            Paste a running configuration or Syslog events, or upload a supported
            text file. NetDoc AI detects the input type and prioritizes operational,
            performance, wireless, and security findings.
          </p>
        </div>

        <div className="mt-10 overflow-hidden rounded-2xl border border-white/10 bg-[#0d131d]">
          <div className="flex flex-col gap-4 border-b border-white/10 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-white">
                Network configuration or Syslog log
              </p>

              <p className="mt-1 text-xs text-slate-600">
                Supported files: .txt, .cfg, .conf, .log
              </p>
            </div>

            <div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.cfg,.conf,.log,text/plain"
                onChange={handleFile}
                className="hidden"
              />

              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-4 py-2.5 text-xs font-medium text-slate-300 transition hover:bg-white/10 hover:text-white"
              >
                <FileUp size={15} />
                Upload log or configuration
              </button>
            </div>
          </div>

          {fileName && (
            <div className="flex items-center justify-between border-b border-white/10 bg-blue-500/5 px-5 py-3">
              <div className="flex items-center gap-2 text-xs text-blue-400">
                <FileText size={14} />
                {fileName}
              </div>

              <button
                type="button"
                onClick={clearConfiguration}
                className="text-slate-600 transition hover:text-white"
                aria-label="Clear configuration"
              >
                <X size={15} />
              </button>
            </div>
          )}

          <div className="p-4">
            <textarea
              value={config}
              onChange={(event) => {
                setConfig(event.target.value);
                setError("");
              }}
              spellCheck="false"
              placeholder={`# Syslog example:
2026-10-23T08:58:12Z CAI-RTR-01 %LINK-3-UPDOWN: Interface GigabitEthernet0/0/2, changed state to down

# Or paste a running configuration:
hostname R1

interface GigabitEthernet0/0
 description LAN
 ip address 192.168.1.1 255.255.255.0
 no shutdown

vlan 10
 name USERS

router ospf 1
 router-id 1.1.1.1`}
              className="h-[420px] w-full resize-y rounded-xl border border-white/10 bg-[#070b12] p-5 font-mono text-xs leading-6 text-slate-300 outline-none transition placeholder:text-slate-700 focus:border-blue-500/40 focus:ring-1 focus:ring-blue-500/10 sm:text-sm"
            />

            {error && (
              <div className="mt-4 rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-3 text-xs text-red-400">
                {error}
              </div>
            )}

            <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <p className="max-w-xl text-xs leading-5 text-slate-600">
                Configuration content is sent to the NetDoc AI analysis API for
                processing.
              </p>

              <button
                type="button"
                onClick={analyzeNetwork}
                disabled={loading || !config.trim()}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {loading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Play size={15} />
                    Analyze configuration
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analyze;
