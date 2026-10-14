
function VlanList({ vlans }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="mb-5">
        <h3 className="text-xl font-semibold">
          VLAN Analysis
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          VLANs detected in the configuration
        </p>
      </div>

      {vlans.length === 0 ? (
        <div className="rounded-xl bg-slate-950 p-5 text-sm text-slate-400">
          No VLANs detected.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-800 text-xs uppercase text-slate-500">
                <th className="px-4 py-3">VLAN ID</th>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>

            <tbody>
              {vlans.map((vlan, index) => (
                <tr
                  key={index}
                  className="border-b border-slate-800/50 last:border-0"
                >
                  <td className="px-4 py-4 font-semibold text-white">
                    {vlan.id}
                  </td>

                  <td className="px-4 py-4 text-slate-300">
                    {vlan.name || "Unnamed"}
                  </td>

                  <td className="px-4 py-4">
                    <span className="rounded-full bg-green-500/10 px-3 py-1 text-xs font-semibold text-green-400">
                      Configured
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default VlanList;

