from enum import Enum
class SupplierOnboardingStatus(str, Enum):
    SYNCING_TO_SAP = "syncing_to_sap"
    COMPLETED = "completed"
    FAILED = "failed"
