import {
  NavLink,
  Outlet,
} from "react-router-dom";

export function Layout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">AI</span>
          <div>
            <strong>Supplier Master</strong>
            <small>Operations Console</small>
          </div>
        </div>

        <nav className="main-nav">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              isActive ? "active" : ""
            }
          >
            <span>▦</span>
            Dashboard
          </NavLink>

          <NavLink
            to="/suppliers"
            className={({ isActive }) =>
              isActive ? "active" : ""
            }
          >
            <span>◫</span>
            Suppliers
          </NavLink>

          <NavLink
            to="/policies/ingest"
            className={({ isActive }) =>
              isActive ? "active" : ""
            }
          >
            <span>◇</span>
            Policy Ingest
          </NavLink>

          <NavLink
            to="/suppliers/new"
            className={({ isActive }) =>
              isActive ? "active" : ""
            }
          >
            <span>＋</span>
            New Supplier
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <div className="environment-dot" />
          Local environment
        </div>
      </aside>

      <main className="content">
        <header className="topbar">
          <div>
            <span className="eyebrow">
              Supplier Master AI
            </span>
          </div>

          <div className="topbar-status">
            <span className="environment-dot" />
            API Gateway
          </div>
        </header>

        <div className="page-container">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
