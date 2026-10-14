import { ArrowUpRight } from "lucide-react";
import { Link } from "react-router-dom";

function Footer() {
  return (
    <footer className="border-t border-white/10 bg-[#070b12]">
      <div className="mx-auto max-w-7xl px-6 py-12 lg:px-8">
        <div className="grid gap-10 md:grid-cols-3">
          {/* Brand */}
          <div>
            <Link to="/" className="inline-flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-sm font-bold text-white">
                N
              </div>

              <span className="text-lg font-bold text-white">
                NetDoc<span className="text-blue-400">AI</span>
              </span>
            </Link>

            <p className="mt-4 max-w-sm text-sm leading-6 text-slate-400">
              Understand your network without the manual work. Analyze,
              document, and improve Cisco configurations faster.
            </p>
          </div>

          {/* Product */}
          <div>
            <h3 className="text-sm font-semibold text-white">Product</h3>

            <div className="mt-4 flex flex-col gap-3">
              <Link
                to="/analyze"
                className="text-sm text-slate-400 transition hover:text-white"
              >
                Analyze
              </Link>

              <Link
                to="/dashboard"
                className="text-sm text-slate-400 transition hover:text-white"
              >
                Dashboard
              </Link>

              <Link
                to="/docs"
                className="text-sm text-slate-400 transition hover:text-white"
              >
                Documentation
              </Link>
            </div>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-sm font-semibold text-white">Resources</h3>

            <div className="mt-4 flex flex-col gap-3">
              <Link
                to="/docs"
                className="inline-flex items-center gap-1 text-sm text-slate-400 transition hover:text-white"
              >
                Getting started
                <ArrowUpRight size={14} />
              </Link>

              <a
                href="https://github.com/"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-sm text-slate-400 transition hover:text-white"
              >
                GitHub
                <ArrowUpRight size={14} />
              </a>
            </div>
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-3 border-t border-white/10 pt-6 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <p>© {new Date().getFullYear()} NetDocAI. All rights reserved.</p>

          <p>Built for network engineers.</p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
