import { Link } from "react-router-dom";
import {
  ArrowRight,
  CheckCircle2,
  FileSearch,
  ShieldCheck,
  Network,
  Upload,
} from "lucide-react";

const features = [
  {
    icon: FileSearch,
    title: "Configuration Analysis",
    description:
      "Parse Cisco configurations into structured network intelligence automatically.",
  },
  {
    icon: ShieldCheck,
    title: "Security Findings",
    description:
      "Identify configuration weaknesses and understand what needs attention.",
  },
  {
    icon: Network,
    title: "Network Visibility",
    description:
      "See interfaces, VLANs, routing, services, ACLs and other network components.",
  },
];

function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-white/10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(37,99,235,0.15),transparent_45%)]" />

        <div className="relative mx-auto max-w-7xl px-5 py-20 sm:px-6 md:py-28">
          <div className="mx-auto max-w-4xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/5 px-4 py-2 text-xs font-medium text-blue-400">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
              Cisco Network Intelligence
            </div>

            <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl md:text-7xl">
              Understand your network
              <span className="block text-blue-500">
                without the manual work.
              </span>
            </h1>

            <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-slate-400 sm:text-lg">
              NetDoc AI analyzes Cisco configurations, identifies security
              risks, maps network components, and turns raw configuration into
              useful documentation.
            </p>

            <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row">
              <Link
                to="/analyze"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3.5 text-sm font-semibold text-white shadow-xl shadow-blue-600/20 transition hover:bg-blue-500"
              >
                Analyze a configuration
                <ArrowRight size={17} />
              </Link>

              <Link
                to="/docs"
                className="inline-flex items-center justify-center rounded-xl border border-white/10 bg-white/5 px-6 py-3.5 text-sm font-semibold text-slate-300 transition hover:bg-white/10 hover:text-white"
              >
                Explore documentation
              </Link>
            </div>
          </div>

          {/* Product preview */}
          <div className="mx-auto mt-16 max-w-5xl">
            <div className="overflow-hidden rounded-2xl border border-white/10 bg-[#0d131d] shadow-2xl shadow-black/40">
              {/* Window bar */}
              <div className="flex items-center gap-2 border-b border-white/10 px-5 py-4">
                <span className="h-2.5 w-2.5 rounded-full bg-red-400/70" />
                <span className="h-2.5 w-2.5 rounded-full bg-yellow-400/70" />
                <span className="h-2.5 w-2.5 rounded-full bg-green-400/70" />

                <span className="ml-3 text-xs text-slate-600">
                  NetDoc AI / Analysis
                </span>
              </div>

              <div className="grid md:grid-cols-[1fr_1.4fr]">
                {/* Configuration */}
                <div className="border-b border-white/10 p-5 md:border-b-0 md:border-r">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
                      Configuration
                    </p>

                    <Upload size={14} className="text-slate-600" />
                  </div>

                  <div className="mt-5 rounded-xl border border-white/5 bg-[#070b12] p-4 font-mono text-[11px] leading-6 text-slate-600">
                    <div className="text-slate-400">hostname R1</div>
                    <div className="mt-1">interface GigabitEthernet0/0</div>
                    <div> ip address 192.168.1.1</div>
                    <div> no shutdown</div>
                    <div className="mt-1">vlan 10</div>
                    <div> name USERS</div>
                    <div className="mt-1">router ospf 1</div>
                    <div> router-id 1.1.1.1</div>
                  </div>
                </div>

                {/* Results */}
                <div className="p-5">
                  <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
                    Analysis
                  </p>

                  <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
                    {[
                      ["90", "Health"],
                      ["2", "Interfaces"],
                      ["2", "VLANs"],
                      ["4", "Findings"],
                    ].map(([value, label]) => (
                      <div
                        key={label}
                        className="rounded-xl border border-white/5 bg-[#070b12] p-4"
                      >
                        <p className="text-xl font-bold text-white">{value}</p>
                        <p className="mt-1 text-[10px] uppercase tracking-wider text-slate-600">
                          {label}
                        </p>
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 rounded-xl border border-green-500/10 bg-green-500/5 p-4">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 size={15} className="text-green-400" />
                      <span className="text-sm font-medium text-green-400">
                        Network health: Excellent
                      </span>
                    </div>

                    <p className="mt-2 text-xs leading-5 text-slate-500">
                      Configuration parsed successfully and network components
                      identified.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="border-b border-white/10 px-5 py-20 sm:px-6">
        <div className="mx-auto max-w-7xl">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-widest text-blue-400">
              What NetDoc AI does
            </p>

            <h2 className="mt-3 text-3xl font-bold text-white sm:text-4xl">
              From raw configuration to network understanding.
            </h2>

            <p className="mt-4 text-sm leading-6 text-slate-500 sm:text-base">
              Stop manually reading hundreds of lines of configuration just to
              understand what a device is doing.
            </p>
          </div>

          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {features.map((feature) => {
              const Icon = feature.icon;

              return (
                <div
                  key={feature.title}
                  className="rounded-2xl border border-white/10 bg-[#0d131d] p-6 transition hover:-translate-y-1 hover:border-blue-500/20"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
                    <Icon size={19} />
                  </div>

                  <h3 className="mt-5 font-semibold text-white">
                    {feature.title}
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-slate-500">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-5 py-20 sm:px-6">
        <div className="mx-auto max-w-5xl overflow-hidden rounded-2xl border border-blue-500/20 bg-blue-500/5 p-8 text-center sm:p-12">
          <h2 className="text-3xl font-bold text-white">
            Ready to analyze your network?
          </h2>

          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-500">
            Upload a Cisco configuration or paste it directly into NetDoc AI and
            get structured network intelligence in seconds.
          </p>

          <Link
            to="/analyze"
            className="mt-7 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
          >
            Start analyzing
            <ArrowRight size={16} />
          </Link>
        </div>
      </section>
    </div>
  );
}

export default Home;
