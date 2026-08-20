import type {
  SupplierOnboarding,
} from "../models/supplier";

interface Props {
  onboarding: SupplierOnboarding;
}

const STEPS = [
  {
    key: "pending",
    title: "Workflow created",
  },
  {
    key: "analyzing",
    title: "AI analysis",
  },
  {
    key: "waiting_human_review",
    title: "Human review",
  },
  {
    key: "syncing_to_sap",
    title: "SAP synchronization",
  },
  {
    key: "completed",
    title: "Onboarding completed",
  },
];

function indexForStatus(status: string) {
  if (status === "rejected" || status === "failed") {
    return 2;
  }

  return Math.max(
    0,
    STEPS.findIndex(
      (step) => step.key === status
    )
  );
}

export function OnboardingTimeline({
  onboarding,
}: Props) {
  const currentIndex = indexForStatus(
    onboarding.status
  );

  return (
    <div className="timeline">
      {STEPS.map((step, index) => {
        const complete =
          index < currentIndex ||
          onboarding.status === "completed";
        const current =
          index === currentIndex &&
          onboarding.status !== "completed";

        return (
          <div
            key={step.key}
            className={`timeline-step ${
              complete ? "complete" : ""
            } ${current ? "current" : ""}`}
          >
            <div className="timeline-marker">
              {complete ? "✓" : index + 1}
            </div>

            <div>
              <strong>{step.title}</strong>

              {current && (
                <small>
                  Current workflow state
                </small>
              )}
            </div>
          </div>
        );
      })}

      {onboarding.status === "failed" && (
        <div className="callout callout-error">
          <strong>Workflow failed</strong>
          <span>
            {onboarding.failure_reason ??
              "No failure reason was provided."}
          </span>
        </div>
      )}

      {onboarding.status === "rejected" && (
        <div className="callout callout-warning">
          <strong>Supplier rejected</strong>
          <span>
            {onboarding.rejection_reason ??
              "No rejection reason was provided."}
          </span>
        </div>
      )}
    </div>
  );
}
