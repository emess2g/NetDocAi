import { useEffect, useRef, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import {
  Activity,
  BarChart3,
  BookOpen,
  FileSearch,
  House,
  LogIn,
  LogOut,
  Menu,
  UserRound,
  ChevronDown,
  X,
  History as HistoryIcon,
} from "lucide-react";
import { supabase } from "../lib/supabase";
import BrandLogo from "./BrandLogo";

function Navbar() {
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);
  const profileRef = useRef(null);

  useEffect(() => {
    let mounted = true;

    async function loadSession() {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (mounted) setSession(session);
    }

    loadSession();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      if (mounted) setSession(nextSession);
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  useEffect(() => {
    function closeOnOutsideClick(event) {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setProfileOpen(false);
      }
    }

    function closeOnEscape(event) {
      if (event.key === "Escape") setProfileOpen(false);
    }

    document.addEventListener("mousedown", closeOnOutsideClick);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("mousedown", closeOnOutsideClick);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, []);

  async function handleSignOut() {
    setLoggingOut(true);
    const { error } = await supabase.auth.signOut();
    setLoggingOut(false);

    if (error) return;

    setProfileOpen(false);
    setMobileOpen(false);
    navigate("/");
  }

  const user = session?.user;
  const email = user?.email || "";
  const displayName =
    user?.user_metadata?.full_name ||
    user?.user_metadata?.name ||
    email.split("@")[0] ||
    "Your account";
  const avatarUrl =
    user?.user_metadata?.avatar_url || user?.user_metadata?.picture || "";
  const initials = displayName
    .split(/[\s._-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("") || "U";

  // Keep private workspace routes out of public navigation until authentication is established.
  const navItems = [
    { to: "/", label: "Home", icon: House, end: true },
    ...(session
      ? [
          { to: "/analyze", label: "Analyze", icon: FileSearch },
          { to: "/dashboard", label: "Dashboard", icon: BarChart3 },
          { to: "/history", label: "History", icon: HistoryIcon },
        ]
      : []),
    { to: "/docs", label: "Docs", icon: BookOpen },
  ];

  const linkClass = ({ isActive }) =>
    `group flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors duration-200 ${
      isActive
        ? "bg-blue-500/10 text-white ring-1 ring-inset ring-blue-400/20"
        : "text-slate-400 hover:bg-white/[0.045] hover:text-white"
    }`;

  return (
    <header className="sticky top-0 z-50 border-b border-white/[0.08] bg-[#070b12]/90 shadow-[0_8px_30px_rgba(0,0,0,0.12)] backdrop-blur-xl">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-blue-400/40 to-transparent" />
      <div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Link
          to="/"
          aria-label="NetDocAi home"
          className="shrink-0 rounded-lg transition-opacity hover:opacity-85"
          onClick={() => setMobileOpen(false)}
        >
          <BrandLogo className="h-10 w-auto" />
        </Link>

        <nav aria-label="Main navigation" className="hidden items-center gap-1 lg:flex">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end} className={linkClass}>
              <Icon size={15} className="opacity-80" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="flex shrink-0 items-center gap-2">
          {session ? (
            <div ref={profileRef} className="relative">
              <button
                type="button"
                onClick={() => setProfileOpen((open) => !open)}
                aria-label="Open profile menu"
                aria-haspopup="menu"
                aria-expanded={profileOpen}
                className="group flex h-11 items-center gap-2 rounded-full border border-white/10 bg-white/[0.035] p-1.5 pr-2.5 transition hover:border-blue-400/35 hover:bg-white/[0.07] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-400"
              >
                <span className="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-blue-400 to-cyan-400 text-xs font-bold text-[#07101d] ring-2 ring-blue-400/20">
                  {avatarUrl ? (
                    <img src={avatarUrl} alt="" className="h-full w-full object-cover" />
                  ) : (
                    initials
                  )}
                </span>
                <span className="hidden max-w-28 truncate text-xs font-medium text-slate-200 sm:block">
                  {displayName}
                </span>
                <ChevronDown size={14} className={`hidden text-slate-500 transition sm:block ${profileOpen ? "rotate-180" : ""}`} />
              </button>

              {profileOpen && (
                <div
                  role="menu"
                  aria-label="Account menu"
                  className="absolute right-0 top-[calc(100%+12px)] z-[60] w-72 overflow-hidden rounded-2xl border border-white/10 bg-[#0c1320] p-2 shadow-[0_20px_70px_rgba(0,0,0,0.55)]"
                >
                  <div className="flex items-center gap-3 rounded-xl bg-white/[0.035] p-3">
                    <span className="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-blue-400 to-cyan-400 text-sm font-bold text-[#07101d]">
                      {avatarUrl ? (
                        <img src={avatarUrl} alt="" className="h-full w-full object-cover" />
                      ) : (
                        initials
                      )}
                    </span>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-white">{displayName}</p>
                      <p className="truncate text-xs text-slate-400">{email}</p>
                    </div>
                  </div>
                  <div className="my-2 h-px bg-white/[0.07]" />
                  <Link
                    to="/profile"
                    role="menuitem"
                    onClick={() => setProfileOpen(false)}
                    className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-slate-300 transition hover:bg-white/[0.06] hover:text-white"
                  >
                    <UserRound size={16} className="text-slate-400" />
                    Profile
                  </Link>
                  <button
                    type="button"
                    role="menuitem"
                    onClick={handleSignOut}
                    disabled={loggingOut}
                    className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm text-slate-300 transition hover:bg-red-400/[0.08] hover:text-red-200 disabled:opacity-60"
                  >
                    <LogOut size={16} className="text-red-300" />
                    {loggingOut ? "Signing out…" : "Sign out"}
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="hidden shrink-0 items-center gap-2 md:flex">
              <Link
                to="/login"
                className="rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-300 transition hover:text-white"
              >
                Sign in
              </Link>
              <Link
                to="/signup"
                className="inline-flex items-center gap-2 rounded-xl bg-blue-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/15 transition hover:bg-blue-400 focus-visible:outline-offset-4"
              >
                Get started
                <span aria-hidden="true">↗</span>
              </Link>
            </div>
          )}

          <button
            type="button"
            onClick={() => setMobileOpen((open) => !open)}
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.035] text-slate-200 transition hover:border-white/20 hover:bg-white/[0.07] lg:hidden"
            aria-label={mobileOpen ? "Close navigation menu" : "Open navigation menu"}
            aria-expanded={mobileOpen}
            aria-controls="mobile-navigation"
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div id="mobile-navigation" className="border-t border-white/[0.08] bg-[#070b12] px-4 pb-6 pt-4 shadow-2xl lg:hidden">
          <div className="mx-auto max-w-7xl">
            <div className="mb-3 flex items-center gap-2 px-3 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-600">
              <Activity size={12} className="text-cyan-400" />
              {session ? "Workspace" : "Explore"}
            </div>
            <nav aria-label="Mobile navigation" className="grid grid-cols-2 gap-2 sm:grid-cols-3">
              {navItems.map(({ to, label, icon: Icon, end }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={end}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) =>
                    `flex min-h-12 items-center gap-2.5 rounded-xl border px-3 py-3 text-sm font-medium transition ${
                      isActive
                        ? "border-blue-400/25 bg-blue-500/10 text-white"
                        : "border-white/[0.07] bg-white/[0.02] text-slate-400 hover:bg-white/[0.05] hover:text-white"
                    }`
                  }
                >
                  <Icon size={16} />
                  {label}
                </NavLink>
              ))}
            </nav>

            {!session && (
              <div className="mt-4 grid grid-cols-2 gap-2 border-t border-white/[0.08] pt-4">
                <Link
                  to="/login"
                  onClick={() => setMobileOpen(false)}
                  className="flex items-center justify-center gap-2 rounded-xl border border-white/10 px-4 py-3 text-sm font-medium text-slate-200 transition hover:bg-white/[0.04]"
                >
                  <LogIn size={16} />
                  Sign in
                </Link>
                <Link
                  to="/signup"
                  onClick={() => setMobileOpen(false)}
                  className="flex items-center justify-center gap-2 rounded-xl bg-blue-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-400"
                >
                  Get started
                  <span aria-hidden="true">↗</span>
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

export default Navbar;
