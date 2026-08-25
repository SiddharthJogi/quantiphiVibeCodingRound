from uuid import UUID
from models import SubscriptionEntity

# In-memory store
SUBSCRIPTIONS: dict[UUID, SubscriptionEntity] = {}
