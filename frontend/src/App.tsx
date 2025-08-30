import { Link, NavLink, Outlet } from "react-router-dom";

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-[radial-gradient(90%_60%_at_10%_-10%,#eef2ff,transparent),radial-gradient(80%_50%_at_90%_-10%,#f1f5f9,transparent)]">
      <header className="sticky top-0 z-30 bg-transparent">
        <div className="page-container h-16 flex items-center justify-center">
          <div className="mx-auto grid h-12 w-full max-w-4xl grid-cols-3 items-center rounded-full bg-white/70 px-3 shadow-md ring-1 ring-black/5 backdrop-blur supports-[backdrop-filter]:bg-white/60">
            {/* Left: Logo */}
            <Link
              to="/"
              className="group inline-flex items-center gap-2 font-semibold tracking-tight justify-self-start no-underline hover:no-underline"
            >
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-white text-slate-700 shadow-sm ring-1 ring-black/10 transition group-hover:scale-105">
                🩺
              </span>
              <span className="text-slate-800 transition group-hover:text-slate-900 group-hover:underline underline-offset-2">
                Baymax
              </span>
            </Link>

            {/* Center: Simple links */}
            <nav className="flex items-center justify-center gap-1 text-sm justify-self-center">
              <NavLink
                to="/intake"
                className={({ isActive }) =>
                  `rounded-md px-3 py-1.5 transition ${
                    isActive
                      ? "text-gray-900"
                      : "text-gray-700 hover:bg-white/50 hover:text-gray-900"
                  }`
                }
              >
                Intake
              </NavLink>
              <NavLink
                to="/doctor"
                className={({ isActive }) =>
                  `rounded-md px-3 py-1.5 transition ${
                    isActive
                      ? "text-gray-900"
                      : "text-gray-700 hover:bg-white/50 hover:text-gray-900"
                  }`
                }
              >
                Doctor
              </NavLink>
            </nav>

            {/* Right: placeholder (future) */}
            <div className="justify-self-end" />
          </div>
        </div>
      </header>
      <main className="flex-1 py-8">
        <div className="page-container">
          <Outlet />
        </div>
      </main>
      <footer className="bg-white/60 backdrop-blur shadow-sm ring-1 ring-black/5">
        <div className="page-container h-14 flex items-center justify-between text-xs text-gray-500">
          <span>© {new Date().getFullYear()} Baymax</span>
          <span>Secure • DPDPA 2023</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
