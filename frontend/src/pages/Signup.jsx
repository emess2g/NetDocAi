import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck, UserRound } from "lucide-react";
import { supabase } from "../lib/supabase";
import AuthShell from "../components/AuthShell";

function Signup() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [error, setError] = useState("");
  const [sentTo, setSentTo] = useState("");

  async function handleSignup(event) {
    event.preventDefault();
    setError("");
    setSentTo("");

    if (!name.trim()) {
      setError("Enter your name to create your account.");
      return;
    }
    if (!email.trim()) {
      setError("Enter a valid email address.");
      return;
    }
    if (password.length < 8) {
      setError("Use at least 8 characters for your password.");
      return;
    }
    if (!/[A-Za-z]/.test(password) || !/[0-9]/.test(password)) {
      setError("For a stronger password, include both letters and numbers.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Your passwords do not match. Please check them and try again.");
      return;
    }

    setLoading(true);
    const { data, error: signupError } = await supabase.auth.signUp({
      email: email.trim(),
      password,
      options: {
        data: { full_name: name.trim() },
        emailRedirectTo: `${window.location.origin}/login?verified=1`,
      },
    });
    setLoading(false);

    if (signupError) {
      setError(signupError.message);
      return;
    }

    if (data.session) {
      navigate("/dashboard", { replace: true });
      return;
    }
    setSentTo(email.trim());
  }

  async function handleGoogleSignUp() {
    setError("");
    setGoogleLoading(true);
    const { error: oauthError } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/dashboard` },
    });
    if (oauthError) {
      setError(oauthError.message);
      setGoogleLoading(false);
    }
  }

  if (sentTo) {
    return (
      <AuthShell mode="signup" eyebrow="ONE LAST STEP" title="Check your inbox." subtitle="Verify your email address to activate your NetDoc AI account.">
        <div className="auth-check-email" role="status">
          <span className="auth-check-icon"><Mail size={22} /></span>
          <h2>Verify your email</h2>
          <p>We sent a confirmation link to <strong className="text-slate-100">{sentTo}</strong>. Open the email and follow the link to verify your address. Check your spam folder if it doesn't arrive.</p>
          <div className="flex items-start gap-2 text-[11px] leading-6 text-slate-400"><ShieldCheck size={16} className="mt-1 shrink-0 text-cyan-300" /> For your security, you may need to sign in after confirming your email.</div>
          <Link className="auth-primary-btn no-underline" to="/login">Continue to sign in <ArrowRight size={15} /></Link>
          <button type="button" className="auth-text-link self-center" onClick={() => setSentTo("")}>Use a different email</button>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell mode="signup" eyebrow="CREATE YOUR WORKSPACE" title="Make your network make sense." subtitle="Create an account to turn configurations into clear, useful network documentation.">
      <form className="auth-form" onSubmit={handleSignup}>
        {error && <div className="auth-message" role="alert">{error}</div>}

        <div className="auth-field">
          <label className="auth-label" htmlFor="signup-name">Your name</label>
          <div className="auth-input-wrap">
            <UserRound className="auth-input-icon" aria-hidden="true" />
            <input id="signup-name" className="auth-input" type="text" value={name} onChange={(event) => setName(event.target.value)} placeholder="How should we address you?" autoComplete="name" maxLength={80} required />
          </div>
        </div>

        <div className="auth-field">
          <label className="auth-label" htmlFor="signup-email">Work or personal email</label>
          <div className="auth-input-wrap">
            <Mail className="auth-input-icon" aria-hidden="true" />
            <input id="signup-email" className="auth-input" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@company.com" autoComplete="email" required />
          </div>
        </div>

        <div className="auth-field">
          <label className="auth-label" htmlFor="signup-password">Create password</label>
          <div className="auth-input-wrap">
            <LockKeyhole className="auth-input-icon" aria-hidden="true" />
            <input id="signup-password" className="auth-input" type={showPassword ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="At least 8 characters" autoComplete="new-password" minLength={8} required />
            <button className="auth-password-toggle" type="button" onClick={() => setShowPassword((visible) => !visible)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button>
          </div>
          <p className="auth-field-hint">Use at least 8 characters, including letters and numbers.</p>
        </div>

        <div className="auth-field">
          <label className="auth-label" htmlFor="signup-confirm">Confirm password</label>
          <div className="auth-input-wrap">
            <LockKeyhole className="auth-input-icon" aria-hidden="true" />
            <input id="signup-confirm" className="auth-input" type={showPassword ? "text" : "password"} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} placeholder="Enter your password again" autoComplete="new-password" minLength={8} required />
          </div>
        </div>

        <button className="auth-primary-btn" type="submit" disabled={loading}>
          {loading ? "Creating your account..." : "Create your account"}
          {!loading && <ArrowRight size={16} />}
        </button>

        <div className="auth-divider">or sign up with</div>
        <button className="auth-google-btn" type="button" onClick={handleGoogleSignUp} disabled={googleLoading}>
          <span className="auth-google-g">G</span>
          {googleLoading ? "Connecting to Google..." : "Continue with Google"}
        </button>

        <div className="flex items-center justify-center gap-2 pt-1 text-[10px] text-slate-500"><ShieldCheck size={13} className="text-cyan-300" /> Email verification helps protect your account</div>

        <p className="pt-2 text-center text-[12px] text-slate-500">
          Already have an account?{" "}
          <Link to="/login" className="font-semibold text-sky-300 transition hover:text-sky-200">Sign in</Link>
        </p>
      </form>
    </AuthShell>
  );
}

export default Signup;
