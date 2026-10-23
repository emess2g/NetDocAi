function ServiceSummary({ network }) {
  const security = network?.security || {};
  const nat = network?.nat || {};
  const dhcp = network?.dhcp;
  const cdp = network?.cdp || {};

  const insideInterfaces = nat.inside_interfaces || [];
  const outsideInterfaces = nat.outside_interfaces || [];

  // The backend currently returns DHCP pools as an array.
  const dhcpPools = Array.isArray(dhcp) ? dhcp : dhcp?.pools || [];

  const services = [
    { name: "SSH", enabled: security.ssh === true },
    { name: "Telnet", enabled: security.telnet === true },
    { name: "HTTP", enabled: security.http === true },
    { name: "HTTPS", enabled: security.https === true },
    { name: "DHCP", enabled: dhcpPools.length > 0 },
    {
      name: "NAT",
      enabled: insideInterfaces.length > 0 || outsideInterfaces.length > 0,
    },
    { name: "CDP", enabled: cdp.enabled === true },
  ];

  return (
    <div className="rounded-xl border border-white/10 bg-[#0d131d] p-4">
      <div className="mb-4">
        <p className="text-xs uppercase tracking-widest text-slate-600">
          Services
        </p>
        <h3 className="mt-1 text-sm font-semibold text-white">
          Network services
        </h3>
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {services.map((service) => (
          <div
            key={service.name}
            className="flex items-center justify-between rounded-lg bg-[#070b12] px-3 py-2.5"
          >
            <span className="text-xs text-slate-400">{service.name}</span>
            <span
              className={
                service.enabled
                  ? "text-xs font-semibold text-green-400"
                  : "text-xs font-semibold text-slate-600"
              }
            >
              {service.enabled ? "✓" : "—"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ServiceSummary;
