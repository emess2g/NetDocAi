
function OspfCard({ routing, eigrp, staticRoutes, bgp }) {
  const ospf = routing || null;
  const eigrpData = eigrp || null;
  const staticRouteData = staticRoutes || [];
  const bgpData = bgp || null;

  const ospfNetworks = ospf?.networks || [];
  const ospfPassiveInterfaces = ospf?.passive_interfaces || [];

  const eigrpNetworks = eigrpData?.networks || [];
  const eigrpPassiveInterfaces = eigrpData?.passive_interfaces || [];

  const bgpNeighbors = bgpData?.neighbors || [];
  const bgpNetworks = bgpData?.networks || [];

  const hasRouting =
    ospf ||
    eigrpData ||
    staticRouteData.length > 0 ||
    bgpData;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="mb-5">
        <h3 className="text-xl font-semibold text-white">
          Routing
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          Routing protocols and routes detected on the device
        </p>
      </div>

      {!hasRouting ? (
        <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-sm text-slate-500">
            No routing configuration detected.
          </p>
        </div>
      ) : (
        <div className="space-y-6">

          {/* OSPF */}
          {ospf && (
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
              <div className="mb-4 flex items-center justify-between">
                <h4 className="text-lg font-semibold text-white">
                  OSPF
                </h4>

                <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-400">
                  Configured
                </span>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-500">
                    Process ID
                  </p>

                  <p className="mt-2 font-semibold text-white">
                    {ospf.process_id || "Not configured"}
                  </p>
                </div>

                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-500">
                    Router ID
                  </p>

                  <p className="mt-2 font-semibold text-white">
                    {ospf.router_id || "Not configured"}
                  </p>
                </div>
              </div>

              <div className="mt-5">
                <p className="mb-3 text-sm font-medium text-slate-300">
                  Network Statements
                </p>

                {ospfNetworks.length === 0 ? (
                  <p className="text-sm text-slate-500">
                    No OSPF networks configured.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {ospfNetworks.map((network, index) => (
                      <div
                        key={index}
                        className="rounded-lg border border-slate-800 bg-slate-900 p-3"
                      >
                        <p className="font-mono text-sm text-blue-400">
                          {network.network}
                        </p>

                        <p className="mt-1 text-xs text-slate-500">
                          Wildcard: {network.wildcard || "N/A"} · Area:{" "}
                          {network.area || "N/A"}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-5">
                <p className="mb-3 text-sm font-medium text-slate-300">
                  Passive Interfaces
                </p>

                {ospfPassiveInterfaces.length === 0 ? (
                  <p className="text-sm text-slate-500">
                    No passive interfaces configured.
                  </p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {ospfPassiveInterfaces.map(
                      (interfaceName, index) => (
                        <span
                          key={index}
                          className="rounded-lg bg-slate-800 px-3 py-2 font-mono text-xs text-slate-300"
                        >
                          {interfaceName}
                        </span>
                      )
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* EIGRP */}
          {eigrpData && (
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
              <div className="mb-4 flex items-center justify-between">
                <h4 className="text-lg font-semibold text-white">
                  EIGRP
                </h4>

                <span className="rounded-full bg-purple-500/10 px-3 py-1 text-xs font-semibold text-purple-400">
                  Configured
                </span>
              </div>

              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  Autonomous System
                </p>

                <p className="mt-2 font-semibold text-white">
                  {eigrpData.as_number || "Not configured"}
                </p>
              </div>

              <div className="mt-5">
                <p className="mb-3 text-sm font-medium text-slate-300">
                  Network Statements
                </p>

                {eigrpNetworks.length === 0 ? (
                  <p className="text-sm text-slate-500">
                    No EIGRP networks configured.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {eigrpNetworks.map((network, index) => (
                      <div
                        key={index}
                        className="rounded-lg border border-slate-800 bg-slate-900 p-3"
                      >
                        <p className="font-mono text-sm text-purple-400">
                          {network}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-5">
                <p className="mb-3 text-sm font-medium text-slate-300">
                  Passive Interfaces
                </p>

                {eigrpPassiveInterfaces.length === 0 ? (
                  <p className="text-sm text-slate-500">
                    No passive interfaces configured.
                  </p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {eigrpPassiveInterfaces.map(
                      (interfaceName, index) => (
                        <span
                          key={index}
                          className="rounded-lg bg-slate-800 px-3 py-2 font-mono text-xs text-slate-300"
                        >
                          {interfaceName}
                        </span>
                      )
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Static Routes */}
          {staticRouteData.length > 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
              <div className="mb-4 flex items-center justify-between">
                <h4 className="text-lg font-semibold text-white">
                  Static Routes
                </h4>

                <span className="rounded-full bg-yellow-500/10 px-3 py-1 text-xs font-semibold text-yellow-400">
                  {staticRouteData.length} detected
                </span>
              </div>

              <div className="space-y-2">
                {staticRouteData.map((route, index) => (
                  <div
                    key={index}
                    className="rounded-lg border border-slate-800 bg-slate-900 p-3"
                  >
                    <p className="font-mono text-sm text-yellow-400">
                      {route.destination} {route.mask}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Next hop:{" "}
                      {route.next_hop ||
                        route.exit_interface ||
                        "Not configured"}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* BGP */}
          {bgpData && (
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
              <div className="mb-4 flex items-center justify-between">
                <h4 className="text-lg font-semibold text-white">
                  BGP
                </h4>

                <span className="rounded-full bg-orange-500/10 px-3 py-1 text-xs font-semibold text-orange-400">
                  Configured
                </span>
              </div>

              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  Autonomous System
                </p>

                <p className="mt-2 font-semibold text-white">
                  {bgpData.as_number || "Not configured"}
                </p>
              </div>

              <div className="mt-5">
                <p className="mb-3 text-sm font-medium text-slate-300">
                  Router ID
                </p>

                <p className="font-mono text-sm text-orange-400">
                  {bgpData.router_id || "Not configured"}
                </p>
              </div>

              <div className="mt-5">
                <p className="mb-3 text-sm font-medium text-slate-300">
                  Neighbors
                </p>

                {bgpNeighbors.length === 0 ? (
                  <p className="text-sm text-slate-500">
                    No BGP neighbors configured.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {bgpNeighbors.map((neighbor, index) => (
                      <div
                        key={index}
                        className="rounded-lg border border-slate-800 bg-slate-900 p-3"
                      >
                        <p className="font-mono text-sm text-orange-400">
                          {neighbor.address}
                        </p>

                        <p className="mt-1 text-xs text-slate-500">
                          Remote AS:{" "}
                          {neighbor.remote_as || "N/A"}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-5">
                <p className="mb-3 text-sm font-medium text-slate-300">
                  Network Statements
                </p>

                {bgpNetworks.length === 0 ? (
                  <p className="text-sm text-slate-500">
                    No BGP networks configured.
                  </p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {bgpNetworks.map((network, index) => (
                      <span
                        key={index}
                        className="rounded-lg bg-slate-800 px-3 py-2 font-mono text-xs text-slate-300"
                      >
                        {network}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default OspfCard;
