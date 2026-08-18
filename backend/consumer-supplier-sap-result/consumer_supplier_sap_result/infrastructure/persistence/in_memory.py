class InMemoryWorkflowRepository:
    def __init__(self): self.items = {}
    async def get_by_id(self, workflow_id): return self.items.get(workflow_id)
    async def update(self, workflow): self.items[workflow.workflow_id] = workflow
    async def add(self, workflow): self.items[workflow.workflow_id] = workflow

class InMemoryInboxRepository:
    def __init__(self): self.items = {}
    async def exists(self, message_id): return message_id in self.items
    async def add(self, message_id, event_type): self.items[message_id] = event_type

class InMemorySupplierResultUnitOfWork:
    def __init__(self):
        self.workflows = InMemoryWorkflowRepository()
        self.inbox = InMemoryInboxRepository()
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): return None
    async def commit(self): return None
