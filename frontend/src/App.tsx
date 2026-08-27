import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";
import {
  Layout,
} from "./components/Layout";
import {
  CreateSupplierPage,
} from "./pages/CreateSupplierPage";
import {
  DashboardPage,
} from "./pages/DashboardPage";
import {
  SupplierDetailsPage,
} from "./pages/SupplierDetailsPage";
import {
  SuppliersPage,
} from "./pages/SuppliersPage";
import { IngestPolicyPage } from "./pages/IngestPolicyPage";
import { AgentPage } from "./pages/AgentPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route
            path="/"
            element={<DashboardPage />}
          />
          <Route
            path="/suppliers"
            element={<SuppliersPage />}
          />
          <Route
            path="/agent"
            element={<AgentPage />}
          />
          <Route
            path="/suppliers/new"
            element={
              <CreateSupplierPage />
            }
          />
          <Route path="/policies/ingest" element={<IngestPolicyPage />} />
          <Route
            path="/suppliers/:supplierId"
            element={
              <SupplierDetailsPage />
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
