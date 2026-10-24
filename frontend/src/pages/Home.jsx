import { Link } from "react-router-dom";
import {
  Activity,
  ArrowDownRight,
  ArrowRight,
  Check,
  CheckCircle2,
  ChevronRight,
  FileSearch,
  Network,
  ShieldCheck,
  Sparkles,
  Upload,
  Workflow,
} from "lucide-react";

const features = [
  {
    icon: FileSearch,
    number: "01",
    title: "Configuration, decoded",
    description:
      "Turn dense Cisco CLI output into a clear, structured view of what is configured on each device.",
    accent: "blue",
  },
  {
    icon: ShieldCheck,
    number: "02",
    title: "Findings with evidence",
    description:
      "Surface potential weaknesses and configuration issues with context to help you investigate.",
    accent: "cyan",
  },
  {
    icon: Network,
    number: "03",
    title: "Your network, mapped",
    description:
      "Review interfaces, VLANs, routing, services and security details from one organized report.",
    accent: "violet",
  },
];

const workflow = [
  {
    icon: Upload,
    title: "Bring your config",
    description: "Paste CLI output or upload a supported configuration file.",
  },
  {
    icon: Workflow,
    title: "Analyze the details",
    description: "NetDocAi organizes device data and checks for notable findings.",
  },
  {
    icon: CheckCircle2,
    title: "Work from a clear report",
    description: "Review network details in a format built for troubleshooting and documentation.",
  },
];

function Home() {
  return (
    <main className="overflow-hidden">
      <section className="relative isolate border-b border-white/[0.07]">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute left-1/2 top-[-23rem] h-[42rem] w-[68rem] -translate-x-1/2 rounded-full bg-blue-600/[0.13] blur-[110px]" />
          <div className="absolute right-[-12rem] top-48 h-80 w-80 rounded-full bg-cyan-400/[0.07] blur-[100px]" />
          <div className="absolute inset-0 opacity-[0.14] [background-image:linear-gradient(rgba(148,163,184,0.11)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.11)_1px,transparent_1px)] [background-size:56px_56px] [mask-image:linear-gradient(to_bottom,black,transparent_82%)]" />
        </div>

        <div className="mx-auto max-w-7xl px-4 pb-16 pt-16 sm:px-6 sm:pb-20 sm:pt-20 lg:px-8 lg:pb-24 lg:pt-24">
          <div className="mx-auto max-w-4xl text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-blue-400/20 bg-blue-400/[0.07] px-3.5 py-2 text-xs font-medium text-blue-200 shadow-[0_0_32px_rgba(59,130,246,0.08)]">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-300 opacity-40" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-cyan-300" />
              </span>
              NETWORK INTELLIGENCE, DOCUMENTED
            </div>

            <h1 className="mt-7 text-4xl font-semibold leading-[1.08] tracking-[-0.045em] text-white sm:text-5xl md:text-7xl">
              Make sense of your
              <span className="mt-1 block bg-gradient-to-r from-blue-300 via-blue-400 to-cyan-300 bg-clip-text pb-2 text-transparent">
                network configuration.
              </span>
            </h1>

            <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-slate-400 sm:text-lg sm:leading-8">
              Move from raw Cisco CLI to useful network documentation. Explore
              device details, review potential risks, and understand your
              configuration without manually tracing every line.
            </p>

            <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row">
              <Link
                to="/analyze"
                className="group inline-flex min-h-12 items-center justify-center gap-2 rounded-xl bg-blue-500 px-6 py-3 text-sm font-semibold text-white shadow-[0_10px_35px_rgba(59,130,246,0.2)] transition duration-200 hover:-translate-y-0.5 hover:bg-blue-400 focus-visible:outline-offset-4"
              >
                Analyze a configuration
                <ArrowRight size={16} className="transition-transform group-hover:translate-x-0.5" />
              </Link>
              <Link
                to="/docs"
                className="inline-flex min-h-12 items-center justify-center gap-2 rounded-xl border border-white/[0.11] bg-white/[0.035] px-6 py-3 text-sm font-semibold text-slate-200 transition hover:border-white/20 hover:bg-white/[0.07]"
              >
                Explore the platform
                <ChevronRight size={16} className="text-slate-500" />
              </Link>
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-xs text-slate-500">
              <span className="inline-flex items-center gap-1.5"><Check size={13} className="text-cyan-300" /> Configuration-first workflow</span>
              <span className="hidden h-1 w-1 rounded-full bg-slate-700 sm:block" />
              <span className="inline-flex items-center gap-1.5"><Check size={13} className="text-cyan-300" /> Evidence-led findings</span>
              <span className="hidden h-1 w-1 rounded-full bg-slate-700 sm:block" />
              <span className="inline-flex items-center gap-1.5"><Check size={13} className="text-cyan-300" /> Structured reports</span>
            </div>
          </div>

          <div className="mx-auto mt-14 max-w-5xl sm:mt-16">
            <div className="relative rounded-2xl border border-white/[0.12] bg-[#0b111b]/95 p-2 shadow-[0_30px_100px_rgba(0,0,0,0.45)] sm:rounded-3xl sm:p-3">
              <div className="pointer-events-none absolute -inset-px -z-10 rounded-3xl bg-gradient-to-b from-blue-400/20 via-white/[0.03] to-cyan-400/10 blur-sm" />
              <div className="overflow-hidden rounded-xl border border-white/[0.07] bg-[#080d15] sm:rounded-2xl">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.07] bg-white/[0.018] px-4 py-3 sm:px-5">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1.5" aria-hidden="true">
                      <span className="h-2.5 w-2.5 rounded-full bg-rose-400/70" />
                      <span className="h-2.5 w-2.5 rounded-full bg-amber-300/70" />
                      <span className="h-2.5 w-2.5 rounded-full bg-emerald-400/70" />
                    </div>
                    <span className="text-xs text-slate-500">NetDocAi <span className="px-1 text-slate-700">/</span> Analysis report</span>
                  </div>
                  <span className="inline-flex items-center gap-1.5 rounded-full border border-white/[0.08] bg-white/[0.03] px-2.5 py-1 text-[10px] font-medium text-slate-400">
                    <Activity size={11} className="text-cyan-300" />
                    Illustrative preview
                  </span>
                </div>

                <div className="grid lg:grid-cols-[0.92fr_1.08fr]">
                  <div className="border-b border-white/[0.07] p-4 sm:p-6 lg:border-b-0 lg:border-r">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">Source configuration</p>
                        <p className="mt-1.5 text-sm font-medium text-slate-200">branch-router.cfg</p>
                      </div>
                      <span className="rounded-lg border border-white/[0.08] bg-white/[0.035] p-2 text-slate-500"><FileSearch size={16} /></span>
                    </div>

                    <div className="mt-5 overflow-hidden rounded-xl border border-white/[0.07] bg-[#05080e] p-4 font-mono text-[10px] leading-[2] sm:text-[11px]">
                      <p><span className="mr-3 text-slate-700">01</span><span className="text-cyan-300">hostname</span> <span className="text-slate-200">BRANCH-R1</span></p>
                      <p><span className="mr-3 text-slate-700">02</span><span className="text-blue-300">interface</span> <span className="text-slate-300">GigabitEthernet0/0</span></p>
                      <p><span className="mr-3 text-slate-700">03</span><span className="text-slate-500"> description Uplink</span></p>
                      <p><span className="mr-3 text-slate-700">04</span><span className="text-blue-200"> ip address</span> <span className="text-slate-300">192.168.10.1 255.255.255.0</span></p>
                      <p><span className="mr-3 text-slate-700">05</span><span className="text-emerald-300"> no shutdown</span></p>
                      <p className="mt-1"><span className="mr-3 text-slate-700">06</span><span className="text-blue-300">router ospf</span> <span className="text-slate-300">10</span></p>
                      <p><span className="mr-3 text-slate-700">07</span><span className="text-slate-500"> router-id 1.1.1.1</span></p>
                      <p className="mt-1"><span className="mr-3 text-slate-700">08</span><span className="text-blue-300">vlan</span> <span className="text-slate-300">20</span></p>
                      <p><span className="mr-3 text-slate-700">09</span><span className="text-slate-500"> name USERS</span></p>
                      <div className="mt-3 flex items-center gap-2 border-t border-white/[0.06] pt-3 text-[10px] text-slate-600">
                        <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
                        Example configuration snippet
                      </div>
                    </div>
                  </div>

                  <div className="p-4 sm:p-6">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">Structured overview</p>
                        <p className="mt-1.5 text-sm font-medium text-slate-200">Network report</p>
                      </div>
                      <span className="inline-flex items-center gap-1.5 rounded-full border border-cyan-400/15 bg-cyan-400/[0.06] px-2.5 py-1 text-[10px] text-cyan-200">
                        <Sparkles size={11} /> Organized
                      </span>
                    </div>

                    <div className="mt-5 grid grid-cols-2 gap-2.5 sm:grid-cols-4">
                      {[
                        { value: "01", label: "Device", color: "text-white" },
                        { value: "02", label: "Interfaces", color: "text-blue-300" },
                        { value: "01", label: "VLAN", color: "text-cyan-300" },
                        { value: "04", label: "Sections", color: "text-violet-300" },
                      ].map((item) => (
                        <div key={item.label} className="rounded-xl border border-white/[0.07] bg-white/[0.025] p-3 sm:p-3.5">
                          <p className={`text-xl font-semibold tracking-tight ${item.color}`}>{item.value}</p>
                          <p className="mt-1 text-[10px] text-slate-500">{item.label}</p>
                        </div>
                      ))}
                    </div>

                    <div className="mt-3 rounded-xl border border-white/[0.07] bg-white/[0.02] p-4">
                      <div className="flex items-start gap-3">
                        <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-emerald-400/15 bg-emerald-400/[0.07] text-emerald-300"><CheckCircle2 size={16} /></span>
                        <div className="min-w-0 flex-1">
                          <p className="text-xs font-semibold text-slate-200">Configuration details organized</p>
                          <p className="mt-1 text-[11px] leading-5 text-slate-500">Device identity, interface details, VLANs and routing information can be reviewed in dedicated report sections.</p>
                        </div>
                      </div>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-2">
                      {["Interfaces", "VLANs", "Routing", "Security"].map((item) => (
                        <span key={item} className="rounded-lg border border-white/[0.07] bg-white/[0.025] px-2.5 py-1.5 text-[10px] text-slate-400">{item}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <p className="mt-4 text-center text-[11px] text-slate-600">Product preview uses sample data for illustration; results depend on the configuration analyzed.</p>
          </div>
        </div>
      </section>

      <section className="border-b border-white/[0.07] px-4 py-16 sm:px-6 sm:py-20 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
            <div className="max-w-2xl">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">Built for network work</p>
              <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">Less time decoding. More time understanding.</h2>
            </div>
            <p className="max-w-md text-sm leading-6 text-slate-500">A practical workspace for turning device configuration into information you can inspect, explain, and document.</p>
          </div>

          <div className="mt-10 grid gap-3 md:grid-cols-3">
            {features.map(({ icon: Icon, number, title, description, accent }) => (
              <article key={title} className="group relative overflow-hidden rounded-2xl border border-white/[0.08] bg-[#0b111b] p-6 transition duration-300 hover:-translate-y-1 hover:border-blue-400/25 hover:bg-[#0d1521] sm:p-7">
                <div className="flex items-center justify-between">
                  <span className={`flex h-11 w-11 items-center justify-center rounded-xl border ${
                    accent === "cyan" ? "border-cyan-300/15 bg-cyan-300/[0.07] text-cyan-200" :
                    accent === "violet" ? "border-violet-300/15 bg-violet-300/[0.07] text-violet-200" :
                    "border-blue-300/15 bg-blue-300/[0.07] text-blue-200"
                  }`}><Icon size={19} /></span>
                  <span className="font-mono text-xs text-slate-700">{number}</span>
                </div>
                <h3 className="mt-6 text-base font-semibold text-white">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>
                <div className="mt-6 flex items-center gap-1.5 text-xs font-medium text-slate-500 transition group-hover:text-blue-300">
                  Explore the workflow <ArrowDownRight size={13} className="transition-transform group-hover:translate-x-0.5 group-hover:translate-y-0.5" />
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="border-b border-white/[0.07] px-4 py-16 sm:px-6 sm:py-20 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">A clearer workflow</p>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">From config to clarity in three steps.</h2>
            <p className="mt-4 text-sm leading-6 text-slate-500 sm:text-base">Keep the workflow straightforward, with the important details easy to find.</p>
          </div>

          <div className="mt-10 grid gap-3 md:grid-cols-3">
            {workflow.map(({ icon: Icon, title, description }, index) => (
              <div key={title} className="relative rounded-2xl border border-white/[0.08] bg-white/[0.02] p-6 sm:p-7">
                <div className="flex items-center justify-between">
                  <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/[0.05] text-blue-200"><Icon size={18} /></span>
                  <span className="font-mono text-xs text-slate-600">STEP 0{index + 1}</span>
                </div>
                <h3 className="mt-5 text-sm font-semibold text-white">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
        <div className="relative mx-auto max-w-5xl overflow-hidden rounded-3xl border border-blue-400/20 bg-[#0b1421] px-6 py-10 text-center sm:px-12 sm:py-14">
          <div aria-hidden="true" className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(59,130,246,0.17),transparent_65%)]" />
          <div className="relative">
            <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-blue-300/20 bg-blue-400/[0.08] text-blue-200"><Network size={21} /></span>
            <p className="mt-5 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-200">Start with a configuration</p>
            <h2 className="mx-auto mt-3 max-w-2xl text-3xl font-semibold tracking-tight text-white sm:text-4xl">Your network has a story. Make it easier to read.</h2>
            <p className="mx-auto mt-4 max-w-xl text-sm leading-6 text-slate-400">Bring a supported configuration into NetDocAi and start exploring a more structured view of your network.</p>
            <Link to="/analyze" className="group mt-7 inline-flex min-h-12 items-center justify-center gap-2 rounded-xl bg-blue-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/15 transition hover:-translate-y-0.5 hover:bg-blue-400">
              Open analyzer <ArrowRight size={16} className="transition-transform group-hover:translate-x-0.5" />
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}

export default Home;
