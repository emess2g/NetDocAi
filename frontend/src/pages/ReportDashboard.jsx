import { useMemo, useState } from "react";
import FindingCard from "../components/FindingCard";
import InterfaceList from "../components/InterfaceList";
import ServiceSummary from "../components/ServiceSummary";
import VlanList from "../components/VlanList";
import OspfCard from "../components/OspfCard";

function ReportDashboard({ network }) {
  const [activeTab, setActiveTab] = useState("summary");
  const [severityFilter, setSeverityFilter] = useState("all");

  const interfaces = Array.isArray(network?.interfaces)
    ? network.interfaces
    : [];

  const vlans = Array.isArray(network?.vlans) ? network.vlans : [];

  const findings = Array.isArray(network?.findings) ? network.findings : [];
  const syslogEvents = Array.isArray(network?.syslog_events) ? network.syslog_events : [];
  const isSyslogReport = network?.report_type === "syslog";

  const acls = Array.isArray(network?.acls) ? network.acls : [];

  const filteredFindings = useMemo(() => {
    if (severityFilter === "all") {
      return findings;
    }

    return findings.filter(
      (finding) =>
        String(finding?.severity || "").toLowerCase() ===
        severityFilter.toLowerCase(),
    );
  }, [findings, severityFilter]);

  const health =
    typeof network?.health === "object" && network.health !== null
      ? network.health
      : {
          score: network?.health_score ?? network?.health ?? 0,
          status: "Unknown",
        };

  const routing = network?.routing || {};

  const ospf = network?.ospf || null;
  const eigrp = network?.eigrp || null;
  const bgp = network?.bgp || null;
  const staticRoutes = network?.static_routes || [];

  const security = network?.security || {};
  const dhcp = network?.dhcp || {};
  const nat = network?.nat || {};
  const cdp = network?.cdp || {};

  const tabs = isSyslogReport
    ? [
        { id: "summary", label: "Summary" },
        { id: "findings", label: "Findings" },
        { id: "events", label: `Events (${syslogEvents.length})` },
      ]
    : [
        { id: "summary", label: "Summary" },
        { id: "findings", label: "Findings" },
        { id: "interfaces", label: "Interfaces" },
        { id: "vlans", label: "VLANs" },
        { id: "routing", label: "Routing" },
        { id: "security", label: "Security" },
      ];

  const criticalCount = findings.filter(
    (finding) => String(finding?.severity || "").toLowerCase() === "critical",
  ).length;

  const highCount = findings.filter(
    (finding) => String(finding?.severity || "").toLowerCase() === "high",
  ).length;

  const mediumCount = findings.filter(
    (finding) => String(finding?.severity || "").toLowerCase() === "medium",
  ).length;

  const lowCount = findings.filter(
    (finding) => String(finding?.severity || "").toLowerCase() === "low",
  ).length;

  const warningCount = findings.filter(
    (finding) => String(finding?.severity || "").toLowerCase() === "warning",
  ).length;

  const infoCount = findings.filter(
    (finding) => String(finding?.severity || "").toLowerCase() === "info",
  ).length;

  const routingProtocols = [];

  if (ospf && Object.keys(ospf).length > 0) {
    routingProtocols.push("OSPF");
  }

  if (eigrp && Object.keys(eigrp).length > 0) {
    routingProtocols.push("EIGRP");
  }

  if (bgp && Object.keys(bgp).length > 0) {
    routingProtocols.push("BGP");
  }

  if (staticRoutes?.length > 0) {
    routingProtocols.push("Static");
  }

  const serviceData = {
    dhcp,
    nat,
    cdp,
    security,
  };

  return (
    <div className="space-y-6">
      {/* HEALTH + DEVICE OVERVIEW */}
      <div className="grid grid-cols-2 gap-x-6 gap-y-5 border-b border-white/10 pb-6 lg:grid-cols-4">
        <div>
          <p className="text-sm text-slate-500">Health score</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-semibold tracking-tight text-white">
              {health.score ?? "—"}
            </span>
            <span className="text-sm text-slate-500">/ 100</span>
          </div>
          <p className="mt-1 text-xs text-slate-400">
            {health.status || "Unknown"}
          </p>
        </div>

        {isSyslogReport ? (
          <>
            <div>
              <p className="text-sm text-slate-500">Syslog events</p>
              <p className="mt-2 text-3xl font-semibold tracking-tight text-white">{syslogEvents.length}</p>
              <p className="mt-1 text-xs text-slate-500">Parsed from log input</p>
            </div>
            <div>
              <p className="text-sm text-slate-500">Devices</p>
              <p className="mt-2 text-3xl font-semibold tracking-tight text-white">{new Set(syslogEvents.map((event) => event.device)).size}</p>
              <p className="mt-1 text-xs text-slate-500">Reporting devices</p>
            </div>
          </>
        ) : (
          <>
            <div>
              <p className="text-sm text-slate-500">Interfaces</p>
              <p className="mt-2 text-3xl font-semibold tracking-tight text-white">{interfaces.length}</p>
              <p className="mt-1 text-xs text-slate-500">Detected</p>
            </div>
            <div>
              <p className="text-sm text-slate-500">VLANs</p>
              <p className="mt-2 text-3xl font-semibold tracking-tight text-white">{vlans.length}</p>
              <p className="mt-1 text-xs text-slate-500">Configured</p>
            </div>
          </>
        )}

        <div>
          <p className="text-sm text-slate-500">Findings</p>
          <p className="mt-2 text-3xl font-semibold tracking-tight text-white">
            {findings.length}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            <span className="text-red-400">{criticalCount} critical</span>
            {" · "}
            <span className="text-orange-400">{highCount} high</span>
          </p>
        </div>
      </div>

      {/* TABS */}
      <div className="space-y-6">
        <div className="overflow-x-auto border-b border-white/10">
          <div className="flex min-w-max">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`border-b-2 px-1 py-3 text-sm transition-colors ${
                  activeTab === tab.id
                    ? "border-blue-500 font-medium text-white"
                    : "border-transparent text-slate-500 hover:text-slate-300"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="pt-6">
          {/* SUMMARY */}
          {activeTab === "summary" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-white">
                  {isSyslogReport ? "Syslog summary" : "Network summary"}
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  {isSyslogReport
                    ? (network?.summary?.overview || "Overview of parsed device events and recommended actions.")
                    : "Overview of the analyzed Cisco configuration."}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-x-6 gap-y-4 border-b border-white/10 pb-5 sm:grid-cols-4">
                {isSyslogReport ? (
                  <>
                    <div className="rounded-xl border border-red-500/10 bg-red-500/5 p-4">
                      <p className="text-xs uppercase tracking-wider text-slate-600">Critical</p>
                      <p className="mt-2 text-2xl font-bold text-red-400">{criticalCount}</p>
                    </div>
                    <div className="rounded-xl border border-orange-500/10 bg-orange-500/5 p-4">
                      <p className="text-xs uppercase tracking-wider text-slate-600">High</p>
                      <p className="mt-2 text-2xl font-bold text-orange-400">{highCount}</p>
                    </div>
                    <div className="rounded-xl border border-yellow-500/10 bg-yellow-500/5 p-4">
                      <p className="text-xs uppercase tracking-wider text-slate-600">Warnings</p>
                      <p className="mt-2 text-2xl font-bold text-yellow-400">{warningCount}</p>
                    </div>
                    <div className="rounded-xl border border-blue-500/10 bg-blue-500/5 p-4">
                      <p className="text-xs uppercase tracking-wider text-slate-600">Informational</p>
                      <p className="mt-2 text-2xl font-bold text-blue-400">{infoCount}</p>
                    </div>
                  </>
                ) : (
                  <>
                <div className="rounded-xl border border-red-500/10 bg-red-500/5 p-4">
                  <p className="text-xs uppercase tracking-wider text-slate-600">
                    Critical
                  </p>

                  <p className="mt-2 text-2xl font-bold text-red-400">
                    {criticalCount}
                  </p>
                </div>

                <div className="rounded-xl border border-orange-500/10 bg-orange-500/5 p-4">
                  <p className="text-xs uppercase tracking-wider text-slate-600">
                    High
                  </p>

                  <p className="mt-2 text-2xl font-bold text-orange-400">
                    {highCount}
                  </p>
                </div>

                <div className="rounded-xl border border-yellow-500/10 bg-yellow-500/5 p-4">
                  <p className="text-xs uppercase tracking-wider text-slate-600">
                    Medium
                  </p>

                  <p className="mt-2 text-2xl font-bold text-yellow-400">
                    {mediumCount}
                  </p>
                </div>

                <div className="rounded-xl border border-blue-500/10 bg-blue-500/5 p-4">
                  <p className="text-xs uppercase tracking-wider text-slate-600">
                    Low
                  </p>

                  <p className="mt-2 text-2xl font-bold text-blue-400">
                    {lowCount}
                  </p>
                </div>
                  </>
                )}
              </div>

              {!isSyslogReport && (
                <div className="grid gap-6 lg:grid-cols-2">
                <div>
                  <h3 className="mb-3 text-sm font-semibold text-white">
                    Interfaces
                  </h3>

                  <InterfaceList interfaces={interfaces} />
                </div>

                <div>
                  <h3 className="mb-3 text-sm font-semibold text-white">
                    Services
                  </h3>

                  <ServiceSummary data={serviceData} />
                </div>
              </div>
              )}

              {vlans.length > 0 && (
                <div>
                  <h3 className="mb-3 text-sm font-semibold text-white">
                    VLANs
                  </h3>

                  <VlanList vlans={vlans} />
                </div>
              )}

              {ospf && Object.keys(ospf).length > 0 && (
                <div>
                  <h3 className="mb-3 text-sm font-semibold text-white">
                    OSPF
                  </h3>

                  <OspfCard ospf={ospf} />
                </div>
              )}
              {isSyslogReport && (
                <div className="rounded-xl border border-white/10 bg-white/[0.02] p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Devices in this log</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {[...new Set(syslogEvents.map((event) => event.device))].map((device) => (
                      <span key={device} className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-300">{device}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* FINDINGS */}
          {activeTab === "findings" && (
            <div className="space-y-5">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-white">
                    {isSyslogReport ? "Syslog findings" : "Configuration findings"}
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    {isSyslogReport
                      ? "Prioritized event analysis with device, timestamp, raw evidence, and recommended next steps."
                      : "Review issues and observations identified during analysis."}
                  </p>
                </div>

                <select
                  value={severityFilter}
                  onChange={(event) => setSeverityFilter(event.target.value)}
                  className="rounded-lg border border-white/10 bg-[#070b12] px-3 py-2 text-xs text-slate-300 outline-none"
                >
                  <option value="all">All severities</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="warning">Warning</option>
                  <option value="low">Low</option>
                  <option value="info">Informational</option>
                </select>
              </div>

              {filteredFindings.length === 0 ? (
                <div className="rounded-xl border border-white/10 bg-white/[0.02] p-10 text-center">
                  <p className="text-sm text-slate-500">
                    No findings match this filter.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredFindings.map((finding, index) => (
                    <FindingCard key={finding?.id || index} finding={finding} />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* RAW SYSLOG EVENTS */}
          {activeTab === "events" && isSyslogReport && (
            <div className="space-y-4">
              <div>
                <h2 className="text-lg font-semibold text-white">Parsed Syslog events</h2>
                <p className="mt-1 text-sm text-slate-500">Raw messages are retained for traceability. Line numbers refer to the uploaded or pasted input.</p>
              </div>
              {syslogEvents.map((event, index) => (
                <div key={`${event.line_number}-${index}`} className="rounded-xl border border-white/10 bg-white/[0.02] p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-xs font-semibold text-slate-300">{event.device}</span>
                    <time className="text-xs text-slate-500" dateTime={event.timestamp}>{event.timestamp}</time>
                  </div>
                  <p className="mt-2 font-mono text-xs text-blue-300">{event.facility}-{event.severity}-{event.mnemonic}</p>
                  <pre className="mt-3 overflow-x-auto whitespace-pre-wrap break-words text-xs leading-5 text-slate-400">{event.raw}</pre>
                  <p className="mt-2 text-xs text-slate-600">Input line {event.line_number}</p>
                </div>
              ))}
            </div>
          )}

          {/* INTERFACES */}
          {!isSyslogReport && activeTab === "interfaces" && (
            <div className="space-y-5">
              <div>
                <h2 className="text-lg font-semibold text-white">Interfaces</h2>

                <p className="mt-1 text-sm text-slate-500">
                  Interfaces discovered in the configuration.
                </p>
              </div>

              <InterfaceList interfaces={interfaces} />
            </div>
          )}

          {/* VLANS */}
          {!isSyslogReport && activeTab === "vlans" && (
            <div className="space-y-5">
              <div>
                <h2 className="text-lg font-semibold text-white">VLANs</h2>

                <p className="mt-1 text-sm text-slate-500">
                  VLANs discovered in the configuration.
                </p>
              </div>

              {vlans.length > 0 ? (
                <VlanList vlans={vlans} />
              ) : (
                <div className="rounded-xl border border-white/10 bg-white/[0.02] p-10 text-center">
                  <p className="text-sm text-slate-500">No VLANs detected.</p>
                </div>
              )}
            </div>
          )}

          {/* ROUTING */}
          {!isSyslogReport && activeTab === "routing" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-white">Routing</h2>

                <p className="mt-1 text-sm text-slate-500">
                  Routing protocols and routes detected on the device.
                </p>
              </div>

              <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5">
                <p className="text-xs font-semibold uppercase tracking-widest text-slate-600">
                  Protocols detected
                </p>

                <div className="mt-4 flex flex-wrap gap-2">
                  {routingProtocols.length > 0 ? (
                    routingProtocols.map((protocol) => (
                      <span
                        key={protocol}
                        className="rounded-lg border border-blue-500/20 bg-blue-500/5 px-3 py-2 text-xs font-medium text-blue-400"
                      >
                        {protocol}
                      </span>
                    ))
                  ) : (
                    <span className="text-sm text-slate-500">
                      No routing protocols detected.
                    </span>
                  )}
                </div>
              </div>

              {ospf && Object.keys(ospf).length > 0 && <OspfCard ospf={ospf} />}

              {eigrp && Object.keys(eigrp).length > 0 && (
                <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5">
                  <h3 className="font-semibold text-white">EIGRP</h3>

                  <pre className="mt-4 overflow-x-auto rounded-lg bg-[#070b12] p-4 text-xs text-slate-400">
                    {JSON.stringify(eigrp, null, 2)}
                  </pre>
                </div>
              )}

              {bgp && Object.keys(bgp).length > 0 && (
                <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5">
                  <h3 className="font-semibold text-white">BGP</h3>

                  <pre className="mt-4 overflow-x-auto rounded-lg bg-[#070b12] p-4 text-xs text-slate-400">
                    {JSON.stringify(bgp, null, 2)}
                  </pre>
                </div>
              )}

              {staticRoutes?.length > 0 && (
                <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5">
                  <h3 className="font-semibold text-white">Static Routes</h3>

                  <pre className="mt-4 overflow-x-auto rounded-lg bg-[#070b12] p-4 text-xs text-slate-400">
                    {JSON.stringify(staticRoutes, null, 2)}
                  </pre>
                </div>
              )}

              {Object.keys(routing).length > 0 && (
                <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5">
                  <h3 className="font-semibold text-white">Routing Details</h3>

                  <pre className="mt-4 overflow-x-auto rounded-lg bg-[#070b12] p-4 text-xs text-slate-400">
                    {JSON.stringify(routing, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}

          {/* SECURITY */}
          {!isSyslogReport && activeTab === "security" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-white">Security</h2>

                <p className="mt-1 text-sm text-slate-500">
                  Security-related configuration and access-control information.
                </p>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5">
                  <p className="text-xs font-semibold uppercase tracking-widest text-slate-600">
                    Security status
                  </p>

                  <p className="mt-3 text-lg font-semibold text-white">
                    {security?.status ||
                      (security?.enabled ? "Enabled" : "Review required")}
                  </p>

                  <pre className="mt-4 max-h-72 overflow-auto rounded-lg bg-[#070b12] p-4 text-xs text-slate-400">
                    {JSON.stringify(security, null, 2)}
                  </pre>
                </div>

                <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5">
                  <p className="text-xs font-semibold uppercase tracking-widest text-slate-600">
                    ACLs
                  </p>

                  <p className="mt-3 text-2xl font-bold text-white">
                    {acls.length}
                  </p>

                  <p className="mt-1 text-xs text-slate-600">
                    Access control lists detected
                  </p>

                  <pre className="mt-4 max-h-72 overflow-auto rounded-lg bg-[#070b12] p-4 text-xs text-slate-400">
                    {JSON.stringify(acls, null, 2)}
                  </pre>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5">
                  <p className="text-xs uppercase tracking-widest text-slate-600">
                    DHCP
                  </p>

                  <p className="mt-3 text-sm font-semibold text-white">
                    {Object.keys(dhcp).length > 0 ? "Detected" : "Not detected"}
                  </p>
                </div>

                <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5">
                  <p className="text-xs uppercase tracking-widest text-slate-600">
                    NAT
                  </p>

                  <p className="mt-3 text-sm font-semibold text-white">
                    {Object.keys(nat).length > 0 ? "Detected" : "Not detected"}
                  </p>
                </div>

                <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5">
                  <p className="text-xs uppercase tracking-widest text-slate-600">
                    CDP
                  </p>

                  <p className="mt-3 text-sm font-semibold text-white">
                    {cdp?.enabled === false
                      ? "Disabled"
                      : cdp?.enabled === true
                        ? "Enabled"
                        : "Not detected"}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ReportDashboard;
