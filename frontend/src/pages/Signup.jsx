import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabase";

function Signup() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSignup(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!name.trim()) {
      setError("Please enter your name.");
      return;
    }

    if (!email.trim()) {
      setError("Please enter your email.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    const { data, error: signupError } = await supabase.auth.signUp({
      email: email.trim(),
      password,
      options: {
        data: {
          full_name: name.trim(),
        },
      },
    });

    if (signupError) {
      setError(signupError.message);
      setLoading(false);
      return;
    }

    setLoading(false);

    if (data.session) {
      navigate("/dashboard");
      return;
    }

    setSuccess(
      "Account created successfully. Check your email to confirm your account.",
    );
  }

  return (
    <div className="flex min-h-[70vh] items-center justify-center px-6 py-16">
      <div className="w-full max-w-md">
        <div className="text-center">
          <p className="text-sm font-medium uppercase tracking-widest text-blue-400">
            Get started
          </p>

          <h1 className="mt-3 text-3xl font-bold text-white">
            Create your NetDoc AI account
          </h1>

          <p className="mt-3 text-sm text-slate-500">
            Start documenting and analyzing your network configurations.
          </p>
        </div>

        <form
          onSubmit={handleSignup}
          className="mt-8 rounded-2xl border border-white/10 bg-[#0d131d] p-6"
        >
          {error && (
            <div className="mb-5 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-5 rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
              {success}
            </div>
          )}

          <label className="text-sm text-slate-300">Name</label>

          <input
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Your name"
            autoComplete="name"
            className="mt-2 w-full rounded-xl border border-white/10 bg-[#070b12] px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500/50"
          />

          <label className="mt-5 block text-sm text-slate-300">Email</label>

          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            autoComplete="email"
            className="mt-2 w-full rounded-xl border border-white/10 bg-[#070b12] px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500/50"
          />

          <label className="mt-5 block text-sm text-slate-300">Password</label>

          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Create a password"
            autoComplete="new-password"
            className="mt-2 w-full rounded-xl border border-white/10 bg-[#070b12] px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500/50"
          />

          <label className="mt-5 block text-sm text-slate-300">
            Confirm password
          </label>

          <input
            type="password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            placeholder="Repeat your password"
            autoComplete="new-password"
            className="mt-2 w-full rounded-xl border border-white/10 bg-[#070b12] px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500/50"
          />

          <button
            type="submit"
            disabled={loading}
            className="mt-6 w-full rounded-xl bg-blue-600 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Creating account..." : "Create account"}
          </button>

          <p className="mt-5 text-center text-sm text-slate-500">
            Already have an account?{" "}
            <Link
              to="/login"
              className="font-medium text-blue-400 transition hover:text-blue-300"
            >
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Signup;
