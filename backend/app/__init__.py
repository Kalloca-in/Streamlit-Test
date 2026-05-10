"""CiberSpar backend.

Core invariants codified across this package:

- Session data lives only in Redis with a hard TTL ceiling (`SESSION_TTL_SECONDS`).
- Postgres is reserved for catalogs, facilitator config, and aggregated metrics
  with `n >= AGGREGATION_MIN_N`. It must never receive session content.
- The intra-session defense model is built in Redis and dies with the session.
"""

__version__ = "0.1.0"
