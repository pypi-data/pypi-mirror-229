from spackle.constants import FEATURE_TYPE_FLAG, FEATURE_TYPE_LIMIT
from spackle.customer import Customer
from spackle.exceptions import SpackleException
from spackle.pricing_table import PricingTable
from spackle.stores import EdgeStore, MemoryStore, FileStore
from spackle.waiters import wait_for_customer, wait_for_subscription

api_key = None
api_base = "https://api.spackle.so/v1"
edge_base = "https://us-west-2.edge.spackle.so"
schema_version = 1
_store = None


def get_store():
    global _store
    if not _store:
        _store = EdgeStore()
    return _store


def set_store(store):
    global _store
    _store = store
