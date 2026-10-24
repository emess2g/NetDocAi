import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ArrowRight, Eye, EyeOff, KeyRound, LockKeyhole, Mail, ShieldCheck } from "lucide-react";
import { supabase } from "../lib/supabase";
import AuthShell from "../components/AuthShell";

function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [resetMode, setResetMode] = useState(false);
  const [requestResetMode, setRequestResetMode] = useState(false);
  const [resetRequested, setResetRequested] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get("verified") === "1") {
      setSuccess("Email verified. Your account is ready—sign in to continue.");
    }
    if (params.get("reset") === "1") {
      setResetMode(true);
      setSuccess("Choose a new password for your NetDoc AI account.");
    }

    const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""));
    const authError = hashParams.get("error_description");
    if (authError) setError(authError);
  }, [location.search]);

  async function handleLogin(event) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!email.trim() || !password) {
      setError("Enter your email address and password to continue.");
      return;
    }

    setLoading(true);
    const { error: loginError } = await supabase.auth.signInWithPassword({
      email: email.trim(),
      password,
    });
    setLoading(false);

    if (loginError) {
      const message = loginError.message.toLowerCase();
      if (message.includes("email not confirmed")) {
        setError("Please verify your email using the confirmation link we sent before signing in.");
      } else if (message.includes("invalid login credentials")) {
        setError("That email and password combination wasn't recognized. Check them and try again.");
      } else {
        setError(loginError.message);
      }
      return;
    }

    navigate(location.state?.from || "/analyze", { replace: true });
  }

  async function handleGoogleSignIn() {
    setError("");
    setSuccess("");
    setGoogleLoading(true);
    const { error: oauthError } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/analyze` },
    });
    if (oauthError) {
      setError(oauthError.message);
      setGoogleLoading(false);
    }
  }

  async function handleResetRequest(event) {
    event.preventDefault();
    setError("");
    setSuccess("");
    if (!email.trim()) {
      setError("Enter the email address associated with your account.");
      return;
    }
    setLoading(true);
    const { error: resetError } = await supabase.auth.resetPasswordForEmail(email.trim(), {
      redirectTo: `${window.location.origin}/login?reset=1`,
    });
    setLoading(false);
    if (resetError) {
      setError(resetError.message);
      return;
    }
    setResetRequested(true);
    setSuccess("If an account exists for this address, a password reset link is on its way.");
  }

  async function handlePasswordUpdate(event) {
    event.preventDefault();
    setError("");
    setSuccess("");
    if (newPassword.length < 8) {
      setError("Use at least 8 characters for your new password.");
      return;
    }
    setLoading(true);
    const { error: updateError } = await supabase.auth.updateUser({ password: newPassword });
    setLoading(false);
    if (updateError) {
      setError(updateError.message);
      return;
    }
    navigate("/dashboard", { replace: true });
  }

  const title = resetMode ? "Set a new password" : "Good to have you back.";
  const subtitle = resetMode
    ? "Choose a strong password to secure your network workspace."
    : "Sign in to pick up where you left off with your network documentation.";

  return (
    <AuthShell
      mode="login"
      eyebrow={resetMode || requestResetMode ? "ACCOUNT RECOVERY" : "SECURE WORKSPACE ACCESS"}
      title={title}
      subtitle={subtitle}
    >
      {resetRequested ? (
        <div className="auth-check-email" role="status">
          <span className="auth-check-icon"><Mail size={21} /></span>
          <h2>Check your inbox</h2>
          <p>{success}</p>
          <button className="auth-primary-btn" type="button" onClick={() => { setResetRequested(false); setResetMode(false); setRequestResetMode(false); setSuccess(""); }}>
            Back to sign in <ArrowRight size={15} />
          </button>
        </div>
      ) : (
        <form className="auth-form" onSubmit={requestResetMode ? handleResetRequest : resetMode ? handlePasswordUpdate : handleLogin}>
          {error && <div className="auth-message" role="alert">{error}</div>}
          {success && <div className="auth-message auth-message-success" role="status">{success}</div>}

          <div className="auth-field">
            <label className="auth-label" htmlFor="login-email">Email address</label>
            <div className="auth-input-wrap">
              <Mail className="auth-input-icon" aria-hidden="true" />
              <input id="login-email" className="auth-input" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@company.com" autoComplete="email" required />
            </div>
          </div>

          {resetMode ? (
            <div className="auth-field">
              <label className="auth-label" htmlFor="new-password">New password</label>
              <div className="auth-input-wrap">
                <KeyRound className="auth-input-icon" aria-hidden="true" />
                <input id="new-password" className="auth-input" type={showPassword ? "text" : "password"} value={newPassword} onChange={(event) => setNewPassword(event.target.value)} placeholder="At least 8 characters" autoComplete="new-password" minLength={8} required />
                <button className="auth-password-toggle" type="button" onClick={() => setShowPassword((visible) => !visible)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button>
              </div>
              <p className="auth-field-hint">Use 8 or more characters. A unique passphrase is best.</p>
            </div>
          ) : !requestResetMode ? (
            <div className="auth-field">
              <label className="auth-label" htmlFor="login-password">Password</label>
              <div className="auth-input-wrap">
                <LockKeyhole className="auth-input-icon" aria-hidden="true" />
                <input id="login-password" className="auth-input" type={showPassword ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" autoComplete="current-password" required />
                <button className="auth-password-toggle" type="button" onClick={() => setShowPassword((visible) => !visible)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button>
              </div>
              <div className="auth-form-row"><button className="auth-text-link" type="button" onClick={() => { setRequestResetMode(true); setResetMode(false); setError(""); setSuccess(""); }}>Forgot password?</button></div>
            </div>
          ) : null}

          <button className="auth-primary-btn" type="submit" disabled={loading}>
            {loading ? "Please wait..." : resetMode ? "Update password" : requestResetMode ? "Send reset link" : "Sign in securely"}
            {!loading && <ArrowRight size={16} />}
          </button>

          {!resetMode && !requestResetMode && (
            <>
              <div className="auth-divider">or continue with</div>
              <button className="auth-google-btn" type="button" onClick={handleGoogleSignIn} disabled={googleLoading}>
                <span className="auth-google-g">G</span>
                {googleLoading ? "Connecting to Google..." : "Continue with Google"}
              </button>
              <div className="flex items-center justify-center gap-2 pt-1 text-[10px] text-slate-500"><ShieldCheck size={13} className="text-cyan-300" /> Secure sign-in powered by Supabase Auth</div>
            </>
          )}

          <p className="pt-2 text-center text-[12px] text-slate-500">
            {resetMode || requestResetMode ? "Remembered your password? " : "New to NetDoc AI? "}
            <Link to={resetMode || requestResetMode ? "/login" : "/signup"} onClick={() => { setResetMode(false); setRequestResetMode(false); setError(""); setSuccess(""); }} className="font-semibold text-sky-300 transition hover:text-sky-200">
              {resetMode || requestResetMode ? "Back to sign in" : "Create an account"}
            </Link>
          </p>
        </form>
      )}
    </AuthShell>
  );
}

export default Login;
