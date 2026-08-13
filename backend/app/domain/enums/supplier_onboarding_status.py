from enum import Enum


class SupplierOnboardingStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    WAITING_HUMAN_REVIEW = "waiting_human_review"
    SYNCING_TO_SAP = "syncing_to_sap"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"