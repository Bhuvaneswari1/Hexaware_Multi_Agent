from typing import Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class Ticket(BaseModel):
    customer_id: str = Field(pattern=r'^C\d{3}$')
    order_id: str = Field(pattern=r'^ORD\d{4}$')
    message: str = Field(min_length=1, max_length=3000)
    preference: str = Field(default='', max_length=100)


class Route(BaseModel):
    teams: list[Literal['billing', 'tech', 'knowledge', 'escalation']]
    reason: str


class Review(BaseModel):
    passed: bool
    feedback: str


class Decision(BaseModel):
    action: Literal['approve', 'reject', 'edit']
    amount_inr: int | None = Field(default=None, ge=1)
    note: str = Field(default='', max_length=500)


class DeskState(TypedDict, total=False):
    customer_id: str
    order_id: str
    message: str
    preference: str
    history: list[dict]
    profile: dict
    route: list[str]
    route_reason: str
    pending: list[str]
    completed: list[str]
    findings: dict
    plan: list[str]
    draft: str
    review: dict
    revisions: int
    refund_amount: int
    refund_status: str
    decision: dict
    status: str
    response: str
    events: list[str]
