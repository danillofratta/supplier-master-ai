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
            path="/suppliers/new"
            element={
              <CreateSupplierPage />
            }
          />
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
