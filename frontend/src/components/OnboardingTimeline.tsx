import type {
  SupplierOnboarding,
} from "../models/supplier";

interface Props {
  onboarding: SupplierOnboarding;
}

interface TimelineStep {
  key: string;
  title: string;
}

const STEPS: TimelineStep[] = [
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

function indexForStatus(status: string): number {
  if (status === "rejected" || status === "failed") {
    return 2;
  }

  const index = STEPS.findIndex(
    (step) => step.key === status
  );

  return index >= 0 ? index : 0;
}

export function OnboardingTimeline({
  onboarding,
}: Props) {
  const currentIndex = indexForStatus(
    onboarding.status
  );
  const usedHumanReview = Boolean(
    onboarding.service_now_ticket_id
  );

  return (
    <div className="timeline">
      {STEPS.map((step, index) => {
        const humanReviewSkipped =
          step.key === "waiting_human_review" &&
          !usedHumanReview &&
          ["syncing_to_sap", "completed"].includes(
            onboarding.status
          );

        const complete =
          !humanReviewSkipped &&
          (index < currentIndex ||
            onboarding.status === "completed");

        const current =
          index === currentIndex &&
          onboarding.status !== "completed" &&
          !humanReviewSkipped;

        return (
          <div
            key={step.key}
            className={`timeline-step ${
              complete ? "complete" : ""
            } ${current ? "current" : ""} ${
              humanReviewSkipped ? "skipped" : ""
            }`}
          >
            <div className="timeline-marker">
              {complete
                ? "✓"
                : humanReviewSkipped
                  ? "—"
                  : index + 1}
            </div>

            <div>
              <strong>{step.title}</strong>

              {current && (
                <small>
                  Current workflow state
                </small>
              )}

              {humanReviewSkipped && (
                <small>
                  Skipped by the automated decision
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
