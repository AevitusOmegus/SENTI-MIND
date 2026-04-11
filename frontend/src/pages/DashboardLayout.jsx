import { useEffect } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function DashboardLayout() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  // Emergency Quick Hide
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        window.location.replace("https://www.google.com");
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleLogout = async () => {
    await signOut();
    navigate("/login");
  };

  const navLinks = [
    { to: ".", label: "Journal", icon: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg> },
    { to: "heatmap", label: "Mood Heatmap", icon: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/><path d="M16 18h.01"/></svg> },
    { to: "history", label: "History", icon: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> },
    { to: "gratitude", label: "Gratitude Jar", icon: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg> },
    { to: "screener", label: "Screener", icon: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> },
    { to: "wellness", label: "Wellness Tools", icon: <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg> },
  ];

  return (
    <div className="flex h-screen bg-sage-50 bg-dashboard-texture bg-repeat overflow-hidden">
      {/* Sidebar Navigation - Floating Module */}
      <aside className="w-64 bg-white/70 backdrop-blur-2xl border border-sage-200/60 shadow-medical-lg rounded-3xl m-4 flex flex-col z-20 overflow-hidden flex-shrink-0">
        <div className="p-6 border-b border-sage-100/50 backdrop-blur-sm">
          <div className="flex items-center gap-4 mb-2">
            <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center text-white shadow-sm border border-sage-100 overflow-hidden">
               <img src="/logo.png" alt="SentiMind Logo" className="w-full h-full object-cover p-1" />
            </div>
            <span className="font-bold text-xl text-warm-800 tracking-tight">
              Senti<span className="text-sage-600">Mind</span>
            </span>
          </div>
          <div className="mt-3 inline-block">
            <p className="text-[10px] font-semibold text-sage-600 bg-sage-100/50 px-3 py-1 rounded-full truncate max-w-[180px] border border-sage-200/50" title={user?.email}>
              {user?.email}
            </p>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "."}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] ${
                  isActive
                    ? "bg-sage-100 text-sage-800 shadow-sm"
                    : "text-warm-600 hover:bg-sage-50/80 hover:text-sage-700"
                }`
              }
            >
              <span className="text-base">{link.icon}</span>
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-sage-100/50 space-y-2 bg-white/30 backdrop-blur-md">
          {/* Quick Hide Button */}
          <button
            onClick={() => window.location.replace("https://www.google.com")}
            className="flex items-center justify-center gap-2 w-full px-3 py-2.5 text-sm font-semibold text-rose-700 bg-rose-50/80 hover:bg-rose-100 rounded-xl transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] border border-rose-200/50 shadow-sm"
            title="Press Escape to instantly hide this page"
          >
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/></svg> Quick Hide (Esc)
          </button>
          
          <button
            onClick={handleLogout}
            className="flex items-center justify-center gap-2 w-full px-3 py-2.5 text-sm font-medium text-warm-600 hover:bg-warm-100/80 rounded-xl transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
          >
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg> Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto relative scroll-smooth focus:outline-none">
        <div className="max-w-6xl mx-auto py-8 px-8 pb-24">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
