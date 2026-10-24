import { Link } from "react-router-dom";
import { ArrowUpRight, ShieldCheck, Waves } from "lucide-react";
import BrandLogo from "./BrandLogo";
import "./auth.css";

function AuthShell({ children, mode = "login", eyebrow, title, subtitle }) {
  const isSignup = mode === "signup";

  return (
    <main className="auth-page">
      <div className="auth-grid" aria-hidden="true" />
      <div className="auth-glow auth-glow-one" aria-hidden="true" />
      <div className="auth-glow auth-glow-two" aria-hidden="true" />

      <div className="auth-layout">
        <section className="auth-form-side">
          <Link to="/" className="auth-brand" aria-label="NetDocAi home">
            <BrandLogo className="h-10 w-auto" />
          </Link>

          <div className="auth-form-wrap">
            <div className="auth-mobile-kicker"><span className="auth-live-dot" /> NETWORK INTELLIGENCE PLATFORM</div>
            <p className="auth-eyebrow">{eyebrow}</p>
            <h1 className="auth-title">{title}</h1>
            <p className="auth-subtitle">{subtitle}</p>
            {children}
            <p className="auth-legal">
              By continuing, you agree to use NetDoc AI responsibly and protect any sensitive network information you submit.
            </p>
          </div>

          <div className="auth-bottomline">
            <span>© {new Date().getFullYear()} NetDoc AI</span>
            <span className="auth-bottom-status"><span className="auth-live-dot" /> Built for network engineers</span>
          </div>
        </section>

        <aside className="auth-visual-side" aria-label="Network intelligence illustration">
          <div className="auth-visual-topline">
            <span><span className="auth-live-dot" /> SYSTEM ONLINE</span>
            <span>ND / 01</span>
          </div>

          <div className="network-stage">
            <div className="network-orbit orbit-outer" />
            <div className="network-orbit orbit-middle" />
            <div className="network-orbit orbit-inner" />
            <div className="network-plane" />
            <svg className="network-lines" viewBox="0 0 600 560" role="img" aria-label="Animated network nodes connected around a central intelligence core">
              <defs>
                <linearGradient id="networkStroke" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#35d7ff" stopOpacity=".12" />
                  <stop offset="50%" stopColor="#5b8cff" stopOpacity=".8" />
                  <stop offset="100%" stopColor="#35d7ff" stopOpacity=".22" />
                </linearGradient>
                <radialGradient id="coreGlow">
                  <stop offset="0%" stopColor="#6be5ff" stopOpacity=".7" />
                  <stop offset="100%" stopColor="#2463eb" stopOpacity="0" />
                </radialGradient>
              </defs>
              <circle cx="300" cy="275" r="150" fill="url(#coreGlow)" />
              <g className="network-connection">
                <path d="M300 275 L160 160 L95 245 L178 355 L300 275 L425 145 L510 230 L450 390 L300 275 L385 475 L178 355 L95 245" />
                <path d="M160 160 L300 105 L425 145 L385 475 L450 390 L510 230" />
                <path d="M95 245 L220 220 L300 105 M220 220 L300 275 L450 390 M178 355 L220 220" />
                <path d="M300 275 L300 105 M300 275 L385 475 M300 275 L510 230" />
              </g>
              <g className="network-packets">
                <circle r="3"><animateMotion dur="4.8s" repeatCount="indefinite" path="M160 160 L300 275 L450 390" /></circle>
                <circle r="2.5"><animateMotion dur="5.6s" repeatCount="indefinite" path="M95 245 L220 220 L425 145" /></circle>
                <circle r="2.5"><animateMotion dur="4.2s" repeatCount="indefinite" path="M385 475 L300 275 L510 230" /></circle>
              </g>
              <g className="network-nodes">
                <circle cx="160" cy="160" r="8" /><circle cx="95" cy="245" r="7" />
                <circle cx="178" cy="355" r="8" /><circle cx="300" cy="105" r="7" />
                <circle cx="425" cy="145" r="8" /><circle cx="510" cy="230" r="7" />
                <circle cx="450" cy="390" r="8" /><circle cx="385" cy="475" r="7" />
                <circle cx="220" cy="220" r="5" />
              </g>
            </svg>
            <div className="network-core">
              <div className="network-core-ring" />
              <div className="network-core-icon"><BrandLogo className="h-8 w-auto" /></div>
              <span>NETDOC <b>CORE</b></span>
            </div>
            <div className="network-float-card network-card-top">
              <span className="network-card-icon"><Waves size={15} /></span>
              <span><b>Network map</b><small>Topology intelligence</small></span>
              <i className="network-card-pulse" />
            </div>
            <div className="network-float-card network-card-bottom">
              <span className="network-card-icon"><ShieldCheck size={15} /></span>
              <span><b>Config health</b><small>Evidence-based insights</small></span>
              <span className="network-score">98</span>
            </div>
            <div className="network-coordinate">37° 46' 49.3" N<br />122° 25' 09.1" W</div>
          </div>

          <div className="auth-visual-copy">
            <div className="auth-visual-kicker"><span /> {isSignup ? "YOUR NETWORK. CLEARER." : "INTELLIGENCE IN EVERY CONNECTION."}</div>
            <h2>{isSignup ? <>Turn configurations<br />into <span>clarity.</span></> : <>Understand your network.<br /><span>See the bigger picture.</span></>}</h2>
            <p>{isSignup ? "Build a reliable source of truth for your network, one configuration at a time." : "Your network documentation and configuration insights, together in one focused workspace."}</p>
          </div>

          <div className="auth-visual-footer">
            <span>DOCUMENT <i /> ANALYZE <i /> UNDERSTAND</span>
            <span className="auth-footer-link">Explore the platform <ArrowUpRight size={14} /></span>
          </div>
        </aside>
      </div>
    </main>
  );
}

export default AuthShell;
