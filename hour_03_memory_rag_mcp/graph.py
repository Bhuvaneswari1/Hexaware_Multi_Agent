"""Hour 3 keeps supervisor orchestration and supplies persistent state/store and tools."""
from hour_02_orchestration.graph import build as orchestration_graph


def build(ctx, pattern='supervisor', checkpointer=None, store=None):
    return orchestration_graph(ctx, 'supervisor', checkpointer, store)
