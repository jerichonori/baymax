import { Link, Outlet } from "react-router-dom";

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-[radial-gradient(90%_60%_at_10%_-10%,#eef2ff,transparent),radial-gradient(80%_50%_at_90%_-10%,#f1f5f9,transparent)]">
      <header className="sticky top-0 z-30 bg-white/60 backdrop-blur supports-[backdrop-filter]:bg-white/50 shadow-sm ring-1 ring-black/5">
        <div className="page-container h-16 flex items-center justify-between">
          <Link
            to="/"
            className="group inline-flex items-center gap-2 font-semibold tracking-tight"
          >
            <span className="grid h-7 w-7 place-items-center rounded-md bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow-sm transition group-hover:scale-105">
              🩺
            </span>
            <span className="transition group-hover:text-blue-700">Baymax</span>
          </Link>
          <nav className="flex items-center gap-2 text-sm">
            <Link
              to="/intake"
              className="rounded-md px-3 py-2 text-gray-700 transition hover:bg-gray-100 hover:text-gray-900"
            >
              Intake
            </Link>
            <Link
              to="/doctor"
              className="rounded-md px-3 py-2 text-gray-700 transition hover:bg-gray-100 hover:text-gray-900"
            >
              Doctor
            </Link>
            <a
              href="https://example.com/help"
              target="_blank"
              rel="noreferrer"
              className="rounded-md px-3 py-2 text-gray-500 transition hover:bg-gray-100 hover:text-gray-800"
            >
              Help
            </a>
          </nav>
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
