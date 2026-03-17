# SCM bridge status

The repository now contains a first safe LUYS bridge importer.

Current proven path:
- Alchemist ingress in luys-os-core
- SCM outbox generation in luys-os-core
- SCM importer in this repository
- manifest-based validation and traceability

This is not yet a native runtime write into SCM internals.
It is a safe transitional bridge layer.
