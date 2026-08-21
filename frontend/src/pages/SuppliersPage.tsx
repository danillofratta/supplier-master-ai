import {
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  Link,
} from "react-router-dom";
import {
  getSuppliers,
} from "../api/suppliersApi";
import type {
  SupplierListItem,
} from "../models/supplier";
import {
  StatusBadge,
} from "../components/StatusBadge";
import { getApiErrorMessage } from "../api/apiError";

export function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<
    SupplierListItem[]
  >([]);
  const [loading, setLoading] =
    useState(true);
  const [error, setError] =
    useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setError(null);
        setSuppliers(await getSuppliers());
      } catch (error: unknown) {
        setError(
          getApiErrorMessage(
            error,
            "Unable to load suppliers through the API Gateway."
          )
        );
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase();

    if (!term) {
      return suppliers;
    }

    return suppliers.filter((supplier) =>
      [
        supplier.name,
        supplier.email,
        supplier.tax_id,
        supplier.status,
      ].some((value) =>
        value.toLowerCase().includes(term)
      )
    );
  }, [suppliers, search]);

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">
            Supplier management
          </span>
          <h1>Suppliers</h1>
          <p>
            Search and inspect suppliers
            participating in the onboarding
            workflow.
          </p>
        </div>

        <Link
          to="/suppliers/new"
          className="button primary"
        >
          + New Supplier
        </Link>
      </div>

      <section className="panel">
        <div className="toolbar">
          <input
            className="search-input"
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder="Search by name, email, tax ID or status..."
          />

          <span className="record-count">
            {filtered.length} supplier
            {filtered.length === 1
              ? ""
              : "s"}
          </span>
        </div>

        {loading && (
          <div className="empty-state">
            Loading suppliers...
          </div>
        )}

        {error && (
          <div className="callout callout-error">
            {error}
          </div>
        )}

        {!loading &&
          !error &&
          filtered.length === 0 && (
            <div className="empty-state">
              No suppliers match your search.
            </div>
          )}

        {!loading &&
          !error &&
          filtered.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Supplier</th>
                    <th>Tax ID</th>
                    <th>Status</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(
                    (supplier) => (
                      <tr
                        key={
                          supplier.supplier_id
                        }
                      >
                        <td>
                          <div className="supplier-cell">
                            <strong>
                              {supplier.name}
                            </strong>
                            <small>
                              {supplier.email}
                            </small>
                          </div>
                        </td>
                        <td>
                          {supplier.tax_id}
                        </td>
                        <td>
                          <StatusBadge
                            status={
                              supplier.status
                            }
                          />
                        </td>
                        <td className="right">
                          <Link
                            to={`/suppliers/${supplier.supplier_id}`}
                            className="text-link"
                          >
                            Details →
                          </Link>
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          )}
      </section>
    </>
  );
}
