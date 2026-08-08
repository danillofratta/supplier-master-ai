from enum import Enum


class SupplierRecommendedAction(str, Enum):
    APPROVE = "approve"
    HUMAN_REVIEW = "human_review"
    REJECT = "reject"
