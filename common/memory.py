"""LangGraph Store, persisted by a small classroom snapshot adapter."""
import json
from langgraph.store.memory import InMemoryStore


class ProfileMemory:
    def __init__(self, path):
        self.path = path
        self.store = InMemoryStore()
        self.snapshot = json.loads(path.read_text()) if path.exists() else {}
        for customer, value in self.snapshot.items():
            self.store.put(('customers', customer), 'profile', value)

    def get(self, customer: str) -> dict:
        item = self.store.get(('customers', customer), 'profile')
        return dict(item.value) if item else {}

    def put(self, customer: str, value: dict):
        self.store.put(('customers', customer), 'profile', value)
        self.snapshot[customer] = value
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps(self.snapshot, indent=2))
        temp.replace(self.path)
