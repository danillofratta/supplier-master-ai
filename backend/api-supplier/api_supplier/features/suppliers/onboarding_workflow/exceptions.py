from uuid import UUID


class SupplierNotFoundForOnboardingError(Exception):
    def __init__(self, supplier_id: UUID) -> None:
        self.supplier_id = supplier_id
        super().__init__(
            f"Supplier '{supplier_id}' was not found for onboarding."
        )


class SupplierOnboardingWorkflowNotFoundError(Exception):
    def __init__(self, workflow_id: UUID) -> None:
        self.workflow_id = workflow_id
        super().__init__(
            f"Supplier onboarding workflow '{workflow_id}' was not found."
        )


class InvalidSupplierOnboardingTransitionError(Exception):
    pass
