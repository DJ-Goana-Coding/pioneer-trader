# Orphaned Logic Archive

Scripts moved here during the **Citadel Unification & Recovery (Stability
9,293)** sweep. Each file had **zero inbound imports** from any other
Python module, workflow, Dockerfile, shell script, or test in the
repository at the time of archiving. They are preserved for historical
reference rather than deleted, in case any of them needs to be reactivated
later.

| Original path | Archived as | Why it was archived |
| --- | --- | --- |
| `backend/engine/binder.py` | `binder.py` | Stub binder with a mock `Settings` class; no other module imported it. The parent `backend/engine/` package was empty after the move and has been removed. |
| `backend/proxy.py` | `proxy.py` | A separate `FastAPI` app titled "Frankfurt Citadel Proxy"; never imported anywhere and not referenced by any workflow, Dockerfile, or run script. The active proxy logic lives in `backend/services/proxy_service.py`'s replacement (none — see below). |
| `backend/services/proxy_service.py` | `proxy_service.py` | Two-line `ProxyService` stub class (`async def forward(self, path): return {"status": "forwarded"}`) with no callers. |

## Audit method

For every Python file under `backend/` and `src/`, references were
counted with `grep` against:

* All `*.py` files (excluding the file's own definition).
* All workflow YAMLs, shell scripts, Dockerfiles, and JSON manifests.

A file was considered orphaned only when it had **zero** matches across
all of the above. Conservative thresholds were used: any file referenced
by an inventory/documentation report but with one or more real code
references was kept in place.

## Files audited but **not** archived

`src/` contains only JavaScript files (UI Stencil Pack components). They
are part of the documented frontend bundle (see root `README.md`) and
were not moved.

All other `backend/` files had at least one inbound code reference and
were left in place.

## Reactivating an archived file

```bash
git mv docs/archive/orphaned_logic/<file>.py <original/path>/<file>.py
```

Then re-add any imports that were removed when the file was archived.
