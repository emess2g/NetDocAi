
function InterfaceList({ interfaces }) {
  const getModeLabel = (mode) => {
    if (mode === "layer3") return "Layer 3 / Routed";
    if (mode === "access") return "Access";
    if (mode === "trunk") return "Trunk";

    return "Unknown";
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <h3 className="mb-5 text-xl font-semibold">
        Interfaces
      </h3>

      <div className="space-y-3">
        {interfaces.map((interfaceItem, index) => {
          const isUp = interfaceItem.status === "up";

          return (
            <div
              key={index}
              className="rounded-xl bg-slate-950 p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-white">
                    {interfaceItem.name}
                  </p>

                  <p className="mt-1 text-sm text-slate-500">
                    {interfaceItem.description ||
                      "No description"}
                  </p>
                </div>

                <span
                  className={
                    isUp
                      ? "rounded-full bg-green-500/10 px-3 py-1 text-xs font-semibold uppercase text-green-400"
                      : "rounded-full bg-red-500/10 px-3 py-1 text-xs font-semibold uppercase text-red-400"
                  }
                >
                  ● {interfaceItem.status}
                </span>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-4 border-t border-slate-800 pt-4">
                <div>
                  <p className="text-xs uppercase text-slate-500">
                    IP Address
                  </p>

                  <p className="mt-1 text-sm text-slate-300">
                    {interfaceItem.ip_address ||
                      "No IP address"}
                  </p>
                </div>

                <div>
                  <p className="text-xs uppercase text-slate-500">
                    Mode
                  </p>

                  <p className="mt-1 text-sm text-slate-300">
                    {getModeLabel(interfaceItem.mode)}
                  </p>
                </div>
              </div>

              {interfaceItem.mode === "trunk" && (
                <div className="mt-4">
                  <p className="text-xs uppercase text-slate-500">
                    Allowed VLANs
                  </p>

                  <p className="mt-1 text-sm text-slate-300">
                    {interfaceItem.allowed_vlans || "None"}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default InterfaceList;
