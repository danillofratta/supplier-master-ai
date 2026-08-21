import {
  type FormEvent,
  useState,
} from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";
import {
  createSupplier,
} from "../api/suppliersApi";
import type {
  CreateSupplierRequest,
} from "../models/supplier";
import { getApiErrorMessage } from "../api/apiError";

const initialForm: CreateSupplierRequest = {
  name: "",
  email: "",
  phone: "",
  tax_id: "",
  address: {
    street: "",
    city: "",
    state: "",
    zip_code: "",
    country: "Brazil",
  },
};

export function CreateSupplierPage() {
  const navigate = useNavigate();
  const [form, setForm] =
    useState<CreateSupplierRequest>(
      initialForm
    );
  const [saving, setSaving] =
    useState(false);
  const [error, setError] =
    useState<string | null>(null);

  function updateField(
    field:
      | "name"
      | "email"
      | "phone"
      | "tax_id",
    value: string
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function updateAddress(
    field: keyof CreateSupplierRequest["address"],
    value: string
  ) {
    setForm((current) => ({
      ...current,
      address: {
        ...current.address,
        [field]: value,
      },
    }));
  }

  async function submit(
    event: FormEvent
  ) {
    event.preventDefault();
    setSaving(true);
    setError(null);

    try {
      const created =
        await createSupplier(form);

      navigate(
        `/suppliers/${created.supplier_id}`
      );
    } catch (error: unknown) {
      setError(
        getApiErrorMessage(
          error,
          "Unable to create supplier."
        )
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">
            Supplier management
          </span>
          <h1>New Supplier</h1>
          <p>
            Register a supplier before AI
            analysis and onboarding.
          </p>
        </div>

        <Link
          to="/suppliers"
          className="button secondary"
        >
          Cancel
        </Link>
      </div>

      <form
        className="form-layout"
        onSubmit={submit}
      >
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Supplier information</h2>
              <p>
                Core master data used throughout
                the workflow.
              </p>
            </div>
          </div>

          <div className="form-grid">
            <label>
              Supplier name
              <input
                required
                minLength={1}
                maxLength={100}
                value={form.name}
                onChange={(event) =>
                  updateField(
                    "name",
                    event.target.value
                  )
                }
              />
            </label>

            <label>
              Tax ID
              <input
                required
                minLength={5}
                maxLength={30}
                value={form.tax_id}
                onChange={(event) =>
                  updateField(
                    "tax_id",
                    event.target.value
                  )
                }
              />
            </label>

            <label>
              Email
              <input
                required
                type="email"
                value={form.email}
                onChange={(event) =>
                  updateField(
                    "email",
                    event.target.value
                  )
                }
              />
            </label>

            <label>
              Phone
              <input
                required
                value={form.phone}
                onChange={(event) =>
                  updateField(
                    "phone",
                    event.target.value
                  )
                }
              />
            </label>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Address</h2>
              <p>
                Used by compliance rules and
                supplier analysis.
              </p>
            </div>
          </div>

          <div className="form-grid">
            <label className="span-two">
              Street
              <input
                required
                value={form.address.street}
                onChange={(event) =>
                  updateAddress(
                    "street",
                    event.target.value
                  )
                }
              />
            </label>

            <label>
              City
              <input
                required
                value={form.address.city}
                onChange={(event) =>
                  updateAddress(
                    "city",
                    event.target.value
                  )
                }
              />
            </label>

            <label>
              State
              <input
                required
                value={form.address.state}
                onChange={(event) =>
                  updateAddress(
                    "state",
                    event.target.value
                  )
                }
              />
            </label>

            <label>
              ZIP code
              <input
                required
                value={form.address.zip_code}
                onChange={(event) =>
                  updateAddress(
                    "zip_code",
                    event.target.value
                  )
                }
              />
            </label>

            <label>
              Country
              <input
                required
                value={form.address.country}
                onChange={(event) =>
                  updateAddress(
                    "country",
                    event.target.value
                  )
                }
              />
            </label>
          </div>
        </section>

        {error && (
          <div className="callout callout-error">
            {error}
          </div>
        )}

        <div className="form-actions">
          <Link
            to="/suppliers"
            className="button secondary"
          >
            Cancel
          </Link>

          <button
            className="button primary"
            disabled={saving}
          >
            {saving
              ? "Creating..."
              : "Create Supplier"}
          </button>
        </div>
      </form>
    </>
  );
}
