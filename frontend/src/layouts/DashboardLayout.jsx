import { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  Activity,
  BookOpen,
  FileSearch,
  History,
  LogOut,
  Menu,
  Network,
  UserRound,
  X,
} from "lucide-react";
import { supabase } from "../lib/supabase";

const navItems = [
  { to: "/dashboard", label: "Overview", icon: Activity, end: true },
  { to: "/analyze", label: "Analyze config", icon: FileSearch },
  { to: "/history", label: "Analysis history", icon: History },
  { to: "/docs", label: "Documentation", icon: BookOpen },
];

function DashboardLayout() {
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    let mounted = true;
    supabase.auth.getSession().then(({ data }) => {
      if (mounted) setSession(data.session);
    });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      if (mounted) setSession(nextSession);
    });
    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [mobileOpen]);

  async function signOut() {
    setLoggingOut(true);
    const { error } = await supabase.auth.signOut();
    setLoggingOut(false);
    if (!error) navigate("/login");
  }

  const navClass = ({ isActive }) =>
    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-xs font-medium transition " +
    (isActive
      ? "bg-[#172945] text-[#e8f0fa] ring-1 ring-inset ring-[#4585fa]/10 before:absolute before:left-0 before:h-5 before:w-[3px] before:rounded-r before:bg-[#4585fa]"
      : "text-[#8596b0] hover:bg-white/[0.04] hover:text-[#e8f0fa]");

  return (
    <div className="min-h-screen bg-[#090e17] text-[#e8f0fa] lg:flex">
      <aside className="hidden w-[236px] shrink-0 border-r border-[#243040] bg-[#0c111b] lg:sticky lg:top-0 lg:flex lg:h-screen lg:flex-col">
        <Link to="/dashboard" className="flex items-center gap-3 px-6 py-6" aria-label="NetDocAi overview">
          <span className="flex h-9 w-9 items-center justify-center rounded-[11px] bg-[#4585fa] text-lg font-bold text-white">N</span>
          <span className="min-w-0"><span className="block text-base font-bold tracking-tight">NetDocAi</span><span className="mt-0.5 block text-[8px] font-semibold tracking-[0.16em] text-[#8596b0]">NETWORK INTELLIGENCE</span></span>
        </Link>
        <div className="mx-5 border-t border-[#243040]" />
        <p className="px-6 pb-3 pt-6 text-[9px] font-bold tracking-[0.18em] text-[#8596b0]">WORKSPACE</p>
        <nav aria-label="Workspace navigation" className="space-y-1 px-3">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end} className={navClass} onClick={() => setMobileOpen(false)}>
              <Icon size={16} className="shrink-0" />{label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto border-t border-[#243040] p-4">
          <div className="flex min-w-0 items-center gap-3">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-[#243040] bg-[#142438] text-[#3dd4e3]"><UserRound size={16} /></span>
            <div className="min-w-0 flex-1"><p className="truncate text-[11px] font-semibold text-[#e8f0fa]">{session?.user?.email || "Your workspace"}</p><p className="mt-1 text-[9px] text-[#8596b0]">NetDocAi workspace</p></div>
            <button type="button" onClick={signOut} disabled={loggingOut} title="Sign out" aria-label="Sign out" className="rounded-lg p-2 text-[#8596b0] transition hover:bg-red-400/10 hover:text-red-300 disabled:opacity-50"><LogOut size={15} /></button>
          </div>
        </div>
      </aside>

      <div className="min-w-0 flex-1">
        <header className="sticky top-0 z-40 border-b border-[#243040] bg-[#090e17]/95 px-4 py-3 backdrop-blur lg:hidden">
          <div className="flex items-center justify-between gap-3">
            <Link to="/dashboard" className="flex items-center gap-2.5" aria-label="NetDocAi overview">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#4585fa] font-bold">N</span>
              <span className="text-sm font-bold">NetDocAi <span className="font-normal text-[#8596b0]">/ Workspace</span></span>
            </Link>
            <button type="button" onClick={() => setMobileOpen((value) => !value)} aria-expanded={mobileOpen} aria-label={mobileOpen ? "Close workspace menu" : "Open workspace menu"} className="rounded-lg border border-[#243040] p-2 text-[#c7d3e3]">
              {mobileOpen ? <X size={18} /> : <Menu size={18} />}
            </button>
          </div>
          {mobileOpen && (
            <nav aria-label="Mobile workspace navigation" className="mt-4 grid gap-1 border-t border-[#243040] pt-3">
              {navItems.map(({ to, label, icon: Icon, end }) => (
                <NavLink key={to} to={to} end={end} onClick={() => setMobileOpen(false)} className={({ isActive }) => "flex items-center gap-3 rounded-lg px-3 py-3 text-sm " + (isActive ? "bg-[#172945] text-[#e8f0fa]" : "text-[#8596b0] hover:bg-white/5 hover:text-white")}>
                  <Icon size={16} />{label}
                </NavLink>
              ))}
              <div className="flex items-center justify-between border-t border-[#243040] pt-3">
                <span className="max-w-[70%] truncate text-xs text-[#8596b0]">{session?.user?.email || "Your workspace"}</span>
                <button type="button" onClick={signOut} disabled={loggingOut} className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-xs text-[#8596b0] hover:text-red-300"><LogOut size={14} />Sign out</button>
              </div>
            </nav>
          )}
        </header>
        <main className="min-h-[calc(100vh-64px)] lg:min-h-screen"><Outlet /></main>
        <footer className="border-t border-[#243040] px-5 py-4 text-center text-[10px] text-[#65758e] lg:text-left lg:px-8">NETDOC AI · NETWORK INTELLIGENCE, DOCUMENTED</footer>
      </div>
    </div>
  );
}

export default DashboardLayout;
