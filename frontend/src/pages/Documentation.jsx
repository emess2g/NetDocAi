function Documentation() {
  return (
    <div className="px-6 py-16">
      <div className="mx-auto max-w-5xl">
        <p className="text-sm font-medium uppercase tracking-widest text-blue-400">
          Documentation
        </p>

        <h1 className="mt-3 text-4xl font-bold text-white">
          NetDoc AI Documentation
        </h1>

        <p className="mt-4 max-w-2xl text-slate-400">
          Learn how to analyze Cisco configurations, understand findings,
          interpret network health scores, and use NetDoc AI effectively.
        </p>

        <div className="mt-10 grid gap-4 md:grid-cols-2">
          {[
            ["Getting Started", "Learn how to run your first analysis."],
            ["Configuration Analysis", "Understand the configuration parser."],
            ["Security Findings", "Learn how security issues are identified."],
            ["Health Score", "Understand the network health calculation."],
          ].map(([title, description]) => (
            <div
              key={title}
              className="rounded-xl border border-white/10 bg-[#0d131d] p-6"
            >
              <h2 className="font-semibold text-white">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                {description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Documentation;
