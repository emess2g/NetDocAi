import { useEffect, useState } from "react";
import { Mail, ShieldCheck, UserRound } from "lucide-react";
import { supabase } from "../lib/supabase";
import { Link } from "react-router-dom";

function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    supabase.auth.getUser().then(({ data, error }) => {
      if (!mounted) return;
      setUser(error ? null : data.user);
      setLoading(false);
    });

    return () => {
      mounted = false;
    };
  }, []);

  const email = user?.email || "";
  const name =
    user?.user_metadata?.full_name ||
    user?.user_metadata?.name ||
    email.split("@")[0] ||
    "NetDocAi user";
  const avatarUrl =
    user?.user_metadata?.avatar_url || user?.user_metadata?.picture || "";
  const initials =
    name
      .split(/[\s._-]+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0].toUpperCase())
      .join("") || "U";

  return (
    <main className="min-h-[calc(100vh-72px)] bg-[#070b12] px-4 py-10 text-white sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <div className="mb-8">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-blue-400">Account</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">Your profile</h1>
          <p className="mt-2 text-sm text-slate-400">View the account details connected to your NetDocAi workspace.</p>
        </div>

        <section className="overflow-hidden rounded-2xl border border-white/[0.09] bg-[#0b111c] shadow-2xl shadow-black/10">
          <div className="border-b border-white/[0.07] bg-gradient-to-r from-blue-500/[0.10] via-cyan-400/[0.04] to-transparent p-6 sm:p-8">
            <div className="flex items-center gap-4">
              <span className="flex h-16 w-16 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-blue-400 to-cyan-400 text-xl font-bold text-[#07101d] ring-4 ring-blue-400/10">
                {avatarUrl ? <img src={avatarUrl} alt="" className="h-full w-full object-cover" /> : initials}
              </span>
              <div className="min-w-0">
                <h2 className="truncate text-xl font-semibold">{loading ? "Loading profile…" : name}</h2>
                <p className="mt-1 truncate text-sm text-slate-400">{email}</p>
                <span className="mt-3 inline-flex items-center gap-1.5 rounded-full border border-emerald-400/15 bg-emerald-400/[0.07] px-2.5 py-1 text-xs font-medium text-emerald-300">
                  <ShieldCheck size={13} />
                  Authenticated account
                </span>
              </div>
            </div>
          </div>

          <div className="space-y-1 p-4 sm:p-6">
            <div className="flex items-center gap-3 rounded-xl p-3 sm:p-4">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.03] text-slate-300">
                <UserRound size={17} />
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-xs text-slate-500">Display name</p>
                <p className="mt-1 truncate text-sm font-medium text-slate-200">{loading ? "Loading…" : name}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-xl p-3 sm:p-4">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.03] text-slate-300">
                <Mail size={17} />
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-xs text-slate-500">Email address</p>
                <p className="mt-1 truncate text-sm font-medium text-slate-200">{loading ? "Loading…" : email || "No email available"}</p>
              </div>
            </div>
          </div>
        </section>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Link to="/dashboard" className="rounded-xl bg-blue-500 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-400">
            Back to dashboard
          </Link>
          <p className="text-xs text-slate-500">Profile editing and photo uploads aren’t available yet.</p>
        </div>
      </div>
    </main>
  );
}

export default Profile;
