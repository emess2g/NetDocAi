function InterfaceList({ interfaces = [] }) {
  const getModeLabel = (mode) => {
    if (mode === "layer3") return "Layer 3";
    if (mode === "access") return "Access";
    if (mode === "trunk") return "Trunk";
    return "Unknown";
  };

  if (interfaces.length === 0) {
    return (
      <div className="py-10 text-center">
        <p className="text-sm text-slate-400">No interfaces found.</p>
      </div>
    );
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-white">Interfaces</h3>
          <p className="mt-1 text-sm text-slate-500">
            Configured network interfaces
          </p>
        </div>

        <span className="text-sm tabular-nums text-slate-400">
          {interfaces.length} total
        </span>
      </div>

      <div className="divide-y divide-white/[0.07]">
        {interfaces.map((interfaceItem, index) => {
          const isUp = interfaceItem.status?.toLowerCase() === "up";

          return (
            <div
              key={interfaceItem.name || index}
              className="py-4 first:pt-2 last:pb-2"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <p className="break-words text-sm font-medium text-slate-100">
                    {interfaceItem.name || `Interface ${index + 1}`}
                  </p>

                  <p className="mt-1 break-words text-xs text-slate-500">
                    {interfaceItem.description || "No description"}
                  </p>
                </div>

                <span className="inline-flex shrink-0 items-center gap-1.5 text-xs text-slate-400">
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      isUp ? "bg-emerald-400" : "bg-slate-500"
                    }`}
                  />
                  <span
                    className={isUp ? "text-emerald-400" : "text-slate-400"}
                  >
                    {interfaceItem.status || "Unknown"}
                  </span>
                </span>
              </div>

              <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs">
                <div>
                  <span className="text-slate-500">IP </span>
                  <span className="font-mono text-slate-300">
                    {interfaceItem.ip_address || "Unassigned"}
                  </span>
                </div>

                <div>
                  <span className="text-slate-500">Mode </span>
                  <span className="text-slate-300">
                    {getModeLabel(interfaceItem.mode)}
                  </span>
                </div>

                {interfaceItem.access_vlan != null &&
                  interfaceItem.mode === "access" && (
                    <div>
                      <span className="text-slate-500">VLAN </span>
                      <span className="text-slate-300">
                        {interfaceItem.access_vlan}
                      </span>
                    </div>
                  )}

                {interfaceItem.mode === "trunk" && (
                  <div className="min-w-0">
                    <span className="text-slate-500">Allowed VLANs </span>
                    <span className="break-words text-slate-300">
                      {interfaceItem.allowed_vlans || "None"}
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

export default InterfaceList;
