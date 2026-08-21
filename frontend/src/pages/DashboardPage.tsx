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

export function DashboardPage() {
  const [suppliers, setSuppliers] = useState<
    SupplierListItem[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setError(null);
        setSuppliers(await getSuppliers());
      } catch (error: unknown) {
        setError(
          getApiErrorMessage(
            error,
            "Unable to load the dashboard."
          )
        );
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const summary = useMemo(() => {
    const total = suppliers.length;
    const draft = suppliers.filter(
      (item) => item.status === "DRAFT"
    ).length;
    const underReview = suppliers.filter(
      (item) =>
        item.status === "UNDER_REVIEW"
    ).length;
    const approved = suppliers.filter(
      (item) => item.status === "APPROVED"
    ).length;

    return {
      total,
      draft,
      underReview,
      approved,
    };
  }, [suppliers]);

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">
            Operations overview
          </span>
          <h1>Dashboard</h1>
          <p>
            Monitor supplier onboarding,
            compliance review and SAP
            integration.
          </p>
        </div>

        <Link
          className="button primary"
          to="/suppliers/new"
        >
          + New Supplier
        </Link>
      </div>

      {error && (
        <div className="callout callout-error">
          {error}
        </div>
      )}

      <div className="metric-grid">
        <div className="metric-card">
          <span>Total suppliers</span>
          <strong>
            {loading ? "—" : summary.total}
          </strong>
          <small>
            Registered supplier records
          </small>
        </div>

        <div className="metric-card">
          <span>Draft</span>
          <strong>
            {loading ? "—" : summary.draft}
          </strong>
          <small>
            Awaiting workflow start
          </small>
        </div>

        <div className="metric-card">
          <span>Under review</span>
          <strong>
            {loading
              ? "—"
              : summary.underReview}
          </strong>
          <small>
            Compliance processing
          </small>
        </div>

        <div className="metric-card">
          <span>Approved</span>
          <strong>
            {loading ? "—" : summary.approved}
          </strong>
          <small>
            Ready or synchronized
          </small>
        </div>
      </div>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Recent suppliers</h2>
            <p>
              Latest records from the Supplier
              bounded context.
            </p>
          </div>

          <Link
            to="/suppliers"
            className="text-link"
          >
            View all
          </Link>
        </div>

        {loading ? (
          <div className="empty-state">
            Loading suppliers...
          </div>
        ) : suppliers.length === 0 ? (
          <div className="empty-state">
            No suppliers have been created yet.
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Tax ID</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {suppliers
                  .slice(0, 5)
                  .map((supplier) => (
                    <tr
                      key={
                        supplier.supplier_id
                      }
                    >
                      <td>
                        <Link
                          to={`/suppliers/${supplier.supplier_id}`}
                          className="supplier-link"
                        >
                          <strong>
                            {supplier.name}
                          </strong>
                          <small>
                            {supplier.email}
                          </small>
                        </Link>
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
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
