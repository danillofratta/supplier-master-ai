from datetime import UTC, datetime

class InMemoryInboxRepository:
    def __init__(self): self.items = {}
    async def exists(self, message_id): return message_id in self.items
    async def add(self, message_id, event_type): self.items[message_id] = event_type

class InMemoryOperationRepository:
    def __init__(self): self.items = {}
    async def get_by_message_id(self, message_id):
        return next((x for x in self.items.values() if x.message_id == message_id), None)
    async def add(self, operation): self.items[operation.operation_id] = operation
    async def update(self, operation): self.items[operation.operation_id] = operation

class InMemoryOutboxRepository:
    def __init__(self): self.items = {}
    async def add(self, message): self.items[message.message_id] = message

class InMemorySapIntegrationUnitOfWork:
    def __init__(self):
        self.inbox = InMemoryInboxRepository()
        self.operations = InMemoryOperationRepository()
        self.outbox_messages = InMemoryOutboxRepository()
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): return None
    async def commit(self): return None
    async def rollback(self): return None
