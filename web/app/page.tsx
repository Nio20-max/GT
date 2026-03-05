export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="flex w-full max-w-4xl flex-col overflow-hidden rounded-2xl bg-gt-green shadow-2xl md:flex-row">
        {/* Left – Facebook connect */}
        <div className="flex flex-1 flex-col items-center justify-center gap-6 bg-gt-fb-blue/90 p-10">
          <h2 className="text-2xl font-bold text-white">Welcome Back!</h2>
          <p className="text-center text-sm text-white/80">
            Connect with Facebook to sync your progress across devices.
          </p>
          <button
            type="button"
            className="flex items-center gap-2 rounded-lg bg-white px-6 py-3 text-sm font-semibold text-gt-fb-blue transition hover:brightness-95"
          >
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" />
            </svg>
            Connect with Facebook
          </button>
        </div>

        {/* Right – Username / Password */}
        <div className="flex flex-1 flex-col items-center justify-center gap-6 p-10">
          <h2 className="text-2xl font-bold text-gt-accent">Goal Tactics</h2>
          <p className="text-center text-sm text-white/70">
            Sign in with your account
          </p>

          <form className="flex w-full max-w-xs flex-col gap-4">
            <input
              type="text"
              placeholder="Username"
              className="rounded-lg border border-gt-accent/30 bg-gt-bg px-4 py-2 text-sm text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-gt-accent"
            />
            <input
              type="password"
              placeholder="Password"
              className="rounded-lg border border-gt-accent/30 bg-gt-bg px-4 py-2 text-sm text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-gt-accent"
            />
            <button
              type="submit"
              className="rounded-lg bg-gt-accent py-2 text-sm font-semibold text-gt-bg transition hover:brightness-110"
            >
              Sign In
            </button>
          </form>

          <p className="text-xs text-white/50">
            Don&apos;t have an account?{" "}
            <span className="cursor-pointer text-gt-highlight underline">
              Register
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
