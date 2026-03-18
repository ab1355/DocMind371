from enum import Enum
from datetime import datetime, timedelta
from typing import List, Dict

class BidStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COUNTER_OFFERED = "counter_offered"

class AgentBid:
    def __init__(self, agent_id: str, task_id: str):
        self.agent_id = agent_id
        self.task_id = task_id
        self.bid_time = datetime.now()
        self.status = BidStatus.PENDING
        self.requested_deadline_extension = None
        self.offered_load_reduction = None
        self.decline_reason = None

    def accept(self):
        self.status = BidStatus.ACCEPTED
        return self.to_dict()

    def decline(self, reason: str = None):
        self.status = BidStatus.DECLINED
        self.decline_reason = reason
        return self.to_dict()

    def counter_offer(self, deadline_extension_hours: int = None,
                      reduced_tasks: int = None):
        """Agent proposes changes to task terms"""
        self.status = BidStatus.COUNTER_OFFERED
        self.requested_deadline_extension = deadline_extension_hours
        self.offered_load_reduction = reduced_tasks
        return self.to_dict()

    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "status": self.status.value,
            "bid_time": self.bid_time.isoformat(),
            "counter_offer": {
                "deadline_extension_hours": self.requested_deadline_extension,
                "reduce_other_tasks": self.offered_load_reduction
            } if self.status == BidStatus.COUNTER_OFFERED else None
        }

class NegotiationEngine:
    def __init__(self):
        self.bids = []

    def create_bid_request(self, task_id: str, agents: List[str],
                           deadline_hours: int, priority: int):
        """Send bid request to multiple agents"""
        request = {
            "task_id": task_id,
            "agents": agents,
            "deadline_hours": deadline_hours,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "responses": {}
        }
        return request

    def accept_bid(self, bid: AgentBid):
        """Confirm agent assignment"""
        bid.accept()
        return f"Task {bid.task_id} assigned to {bid.agent_id}"

    def handle_counter_offer(self, bid: AgentBid, accept_counter: bool):
        """Handle agent counter-offer"""
        if accept_counter:
            return {
                "status": "accepted",
                "new_deadline": bid.requested_deadline_extension,
                "removed_tasks": bid.offered_load_reduction
            }
        else:
            return {"status": "rejected", "reason": "Counter-offer not accepted"}
