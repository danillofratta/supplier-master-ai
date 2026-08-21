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


class SupplierOnboardingForSupplierNotFoundError(Exception):
    def __init__(self, supplier_id: UUID) -> None:
        self.supplier_id = supplier_id
        super().__init__(
            f"No onboarding workflow was found for supplier '{supplier_id}'."
        )


class SupplierOnboardingAlreadyStartedError(Exception):
    def __init__(
        self,
        supplier_id: UUID,
        workflow_id: UUID,
        status: str,
    ) -> None:
        self.supplier_id = supplier_id
        self.workflow_id = workflow_id
        self.status = status
        super().__init__(
            "Supplier onboarding has already been started "
            f"(workflow '{workflow_id}', status '{status}')."
        )


class InvalidSupplierOnboardingTransitionError(Exception):
    pass
