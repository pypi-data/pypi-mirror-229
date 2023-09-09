from typing import TypedDict, Optional, Dict, Any


class SubscriptionData(TypedDict, total=False):
    input_data: Optional[Dict[str, Any]]
    last_current_index: Optional[int]
    triggered_source: Optional[str]


class Subscription(TypedDict, total=False):
    id: str
    data: Optional[SubscriptionData]
