import { useEffect, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import {
  BarChart3,
  BookOpen,
  FileSearch,
  LogIn,
  LogOut,
  Menu,
  User,
  X,
} from "lucide-react";
import { supabase } from "../lib/supabase";
import BrandLogo from "./BrandLogo";

function Navbar() {
  const navigate = useNavigate();

  const [session, setSession] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function loadSession() {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (mounted) {
        setSession(session);
      }
    }

    loadSession();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      if (mounted) {
        setSession(nextSession);
      }
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  async function handleSignOut() {
    setLoggingOut(true);

    await supabase.auth.signOut();

    setMobileOpen(false);
    setLoggingOut(false);

    navigate("/");
  }

  const navItems = [
    {
      to: "/analyze",
      label: "Analyze",
      icon: FileSearch,
    },
    {
      to: "/dashboard",
      label: "Dashboard",
      icon: BarChart3,
    },
    {
      to: "/docs",
      label: "Documentation",
      icon: BookOpen,
    },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-[#070b12]/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6 lg:px-8">
        <Link
          to="/"
          className="flex items-center gap-2"
          onClick={() => setMobileOpen(false)}
        >
          <BrandLogo className="h-10 w-auto" />
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition ${
                  isActive
                    ? "bg-white/10 text-white"
                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          {session ? (
            <>
              <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2">
                <User size={15} className="text-slate-400" />

                <span className="max-w-40 truncate text-sm text-slate-300">
                  {session.user.email}
                </span>
              </div>

              <button
                type="button"
                onClick={handleSignOut}
                disabled={loggingOut}
                className="flex items-center gap-2 rounded-lg border border-white/10 px-4 py-2 text-sm font-medium text-slate-300 transition hover:border-red-500/30 hover:bg-red-500/10 hover:text-red-300 disabled:opacity-60"
              >
                <LogOut size={16} />
                {loggingOut ? "Signing out..." : "Sign out"}
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-slate-300 transition hover:text-white"
              >
                <LogIn size={16} />
                Sign in
              </Link>

              <Link
                to="/signup"
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500"
              >
                Get started
              </Link>
            </>
          )}
        </div>

        <button
          type="button"
          onClick={() => setMobileOpen((open) => !open)}
          className="rounded-lg p-2 text-slate-300 transition hover:bg-white/5 hover:text-white md:hidden"
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
        >
          {mobileOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {mobileOpen && (
        <div className="border-t border-white/10 bg-[#070b12] px-6 py-5 md:hidden">
          <nav className="flex flex-col gap-2">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-4 py-3 text-sm transition ${
                    isActive
                      ? "bg-white/10 text-white"
                      : "text-slate-400 hover:bg-white/5 hover:text-white"
                  }`
                }
              >
                <Icon size={17} />
                {label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-4 border-t border-white/10 pt-4">
            {session ? (
              <div className="space-y-3">
                <div className="flex items-center gap-2 px-4 text-sm text-slate-400">
                  <User size={16} />
                  <span className="truncate">{session.user.email}</span>
                </div>

                <button
                  type="button"
                  onClick={handleSignOut}
                  disabled={loggingOut}
                  className="flex w-full items-center justify-center gap-2 rounded-lg border border-white/10 px-4 py-3 text-sm font-medium text-slate-300 transition hover:bg-red-500/10 hover:text-red-300 disabled:opacity-60"
                >
                  <LogOut size={16} />
                  {loggingOut ? "Signing out..." : "Sign out"}
                </button>
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                <Link
                  to="/login"
                  onClick={() => setMobileOpen(false)}
                  className="flex items-center justify-center gap-2 rounded-lg border border-white/10 px-4 py-3 text-sm font-medium text-slate-300"
                >
                  <LogIn size={16} />
                  Sign in
                </Link>

                <Link
                  to="/signup"
                  onClick={() => setMobileOpen(false)}
                  className="rounded-lg bg-blue-600 px-4 py-3 text-center text-sm font-semibold text-white"
                >
                  Get started
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
