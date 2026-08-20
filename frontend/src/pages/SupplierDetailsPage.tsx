import {
  useEffect,
  useState,
} from "react";
import {
  Link,
  useParams,
} from "react-router-dom";
import {
  analyzeSupplier,
  getSupplier,
  getSupplierOnboarding,
} from "../api/suppliersApi";
import {
  OnboardingTimeline,
} from "../components/OnboardingTimeline";
import {
  StatusBadge,
} from "../components/StatusBadge";
import type {
  Supplier,
  SupplierAnalysisResponse,
  SupplierOnboarding,
} from "../models/supplier";

export function SupplierDetailsPage() {
  const { supplierId } = useParams<{
    supplierId: string;
  }>();

  const [supplier, setSupplier] =
    useState<Supplier | null>(null);
  const [onboarding, setOnboarding] =
    useState<SupplierOnboarding | null>(
      null
    );
  const [analysis, setAnalysis] =
    useState<SupplierAnalysisResponse | null>(
      null
    );
  const [loading, setLoading] =
    useState(true);
  const [analyzing, setAnalyzing] =
    useState(false);
  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    if (!supplierId) {
      return;
    }

    async function load() {
      try {
        setError(null);

        const [
          supplierResult,
          onboardingResult,
        ] = await Promise.all([
          getSupplier(supplierId!),
          getSupplierOnboarding(
            supplierId!
          ),
        ]);

        setSupplier(supplierResult);
        setOnboarding(onboardingResult);
      } catch {
        setError(
          "Unable to load supplier details."
        );
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [supplierId]);

  async function runAnalysis() {
    if (!supplierId) {
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      const result =
        await analyzeSupplier(supplierId);

      setAnalysis(result);
    } catch (error: any) {
      const detail =
        error?.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : "Unable to analyze supplier."
      );
    } finally {
      setAnalyzing(false);
    }
  }

  if (loading) {
    return (
      <div className="empty-state">
        Loading supplier...
      </div>
    );
  }

  if (error && !supplier) {
    return (
      <div className="callout callout-error">
        {error}
      </div>
    );
  }

  if (!supplier) {
    return (
      <div className="empty-state">
        Supplier not found.
      </div>
    );
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <Link
            to="/suppliers"
            className="text-link"
          >
            ← Suppliers
          </Link>

          <span className="eyebrow">
            Supplier details
          </span>

          <div className="title-row">
            <h1>{supplier.name}</h1>
            <StatusBadge
              status={supplier.status}
            />
          </div>

          <p>
            {supplier.tax_id} ·{" "}
            {supplier.email}
          </p>
        </div>

        <button
          className="button primary"
          onClick={runAnalysis}
          disabled={analyzing}
        >
          {analyzing
            ? "Analyzing..."
            : "Run AI Analysis"}
        </button>
      </div>

      {error && (
        <div className="callout callout-error">
          {error}
        </div>
      )}

      <div className="details-grid">
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Master data</h2>
              <p>
                Supplier information stored in
                the Supplier bounded context.
              </p>
            </div>
          </div>

          <dl className="detail-list">
            <div>
              <dt>Supplier ID</dt>
              <dd>{supplier.supplier_id}</dd>
            </div>
            <div>
              <dt>Tax ID</dt>
              <dd>{supplier.tax_id}</dd>
            </div>
            <div>
              <dt>Email</dt>
              <dd>{supplier.email}</dd>
            </div>
            <div>
              <dt>Phone</dt>
              <dd>{supplier.phone}</dd>
            </div>
            <div>
              <dt>Address</dt>
              <dd>
                {supplier.street},{" "}
                {supplier.city} -{" "}
                {supplier.state},{" "}
                {supplier.zip_code},{" "}
                {supplier.country}
              </dd>
            </div>
          </dl>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Onboarding</h2>
              <p>
                Distributed workflow status.
              </p>
            </div>
          </div>

          {!onboarding ? (
            <div className="empty-state compact">
              No onboarding workflow exists for
              this supplier yet.
            </div>
          ) : (
            <>
              <div className="onboarding-meta">
                <div>
                  <span>Status</span>
                  <StatusBadge
                    status={onboarding.status}
                  />
                </div>

                <div>
                  <span>
                    Correlation ID
                  </span>
                  <code>
                    {
                      onboarding.correlation_id
                    }
                  </code>
                </div>

                {onboarding
                  .sap_business_partner_id && (
                  <div>
                    <span>
                      SAP Business Partner
                    </span>
                    <strong>
                      {
                        onboarding
                          .sap_business_partner_id
                      }
                    </strong>
                  </div>
                )}

                {onboarding
                  .service_now_ticket_id && (
                  <div>
                    <span>
                      ServiceNow ticket
                    </span>
                    <strong>
                      {
                        onboarding
                          .service_now_ticket_id
                      }
                    </strong>
                  </div>
                )}
              </div>

              <OnboardingTimeline
                onboarding={onboarding}
              />
            </>
          )}
        </section>
      </div>

      {analysis && (
        <section className="panel ai-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                AI decision support
              </span>
              <h2>Supplier analysis</h2>
              <p>
                Retrieval + LLM analysis with
                deterministic safety rules.
              </p>
            </div>

            <div className="confidence">
              <strong>
                {Math.round(
                  analysis.confidence * 100
                )}
                %
              </strong>
              <span>Confidence</span>
            </div>
          </div>

          <div className="analysis-grid">
            <div className="analysis-card">
              <span>Risk level</span>
              <strong>
                {analysis.risk_level}
              </strong>
            </div>

            <div className="analysis-card">
              <span>
                Recommended action
              </span>
              <strong>
                {
                  analysis.recommended_action
                }
              </strong>
            </div>
          </div>

          <div className="analysis-summary">
            <h3>Summary</h3>
            <p>{analysis.summary}</p>
          </div>

          <div className="analysis-lists">
            <div>
              <h3>
                Retrieved policies
              </h3>
              {analysis.retrieved_policy_ids
                .length === 0 ? (
                <p className="muted">
                  No policy references returned.
                </p>
              ) : (
                <ul>
                  {analysis.retrieved_policy_ids.map(
                    (item) => (
                      <li key={item}>
                        {item}
                      </li>
                    )
                  )}
                </ul>
              )}
            </div>

            <div>
              <h3>
                Missing documents
              </h3>
              {analysis.missing_documents
                .length === 0 ? (
                <p className="muted">
                  No missing documents.
                </p>
              ) : (
                <ul>
                  {analysis.missing_documents.map(
                    (item) => (
                      <li key={item}>
                        {item}
                      </li>
                    )
                  )}
                </ul>
              )}
            </div>

            <div>
              <h3>
                Policy violations
              </h3>
              {analysis.policy_violations
                .length === 0 ? (
                <p className="muted">
                  No policy violations.
                </p>
              ) : (
                <ul>
                  {analysis.policy_violations.map(
                    (item) => (
                      <li key={item}>
                        {item}
                      </li>
                    )
                  )}
                </ul>
              )}
            </div>
          </div>
        </section>
      )}
    </>
  );
}
