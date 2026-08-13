"""GET /health — liveness + readiness (spec §32).

Production health check must verify API, database, and model:

    {"api": "healthy", "database": "healthy", "model": "loaded"}

TODO:
- Return 200 {"status": "healthy"} minimum.
- Advanced: also ping the DB (SELECT 1) and report model load state.
"""
