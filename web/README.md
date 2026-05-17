# Local Web Adapter

`web/` is an optional local browser interface for the repository's deterministic
tools. It does not own schema rules or hardware decision logic; those remain in
the CLI scripts and skill documents.

## Run

From the repository root:

```bash
python web/run.py
```

The runner binds to `127.0.0.1` and chooses the first free port from
`8000..8099`.

## Verify

```bash
python web/smoke_test.py
python tools/scripts/doctor.py
```

`smoke_test.py` covers the bridge functions and the FastAPI endpoints for
health, record lint, DAG generation, and workbook formatting. `doctor.py`
includes the smoke test in the repository-wide validation loop.
