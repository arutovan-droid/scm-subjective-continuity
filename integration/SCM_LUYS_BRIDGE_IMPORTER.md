# SCM LUYS Bridge Importer

## Status
Safe first importer for Alchemist continuity payloads.

## Purpose
This script reads outbox JSON files produced by luys-os-core and imports them into the SCM repository in a non-destructive way.

## Current behavior
The importer:

1. reads from:
   - ~/Desktop/luys-os-core/integration/outbox/scm
2. validates payload shape against the current bridge contract
3. copies each file into:
   - integration/inbox/scm_from_luys
4. appends an import record into:
   - integration/imported/scm_from_luys_manifest.jsonl
5. moves the source file into:
   - integration/imported/scm_from_luys

## Important
This importer does **not** yet write directly into the internal SCM memory engine.
It is a safe bridge-reader stage.

## Script
- scripts/import_alchemist_outbox.py

## Next step
After the bridge contract is stable, replace inbox/imported-only behavior with a real SCM runtime adapter.
