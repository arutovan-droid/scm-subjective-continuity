from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


SOURCE_DIR = Path.home() / "Desktop" / "luys-os-core" / "integration" / "outbox" / "scm"
INBOX_DIR = Path("integration/inbox/scm_from_luys")
IMPORTED_DIR = Path("integration/imported/scm_from_luys")
MANIFEST_PATH = Path("integration/imported/scm_from_luys_manifest.jsonl")


REQUIRED_TOP_LEVEL_FIELDS = [
    "operator_id",
    "session_id",
    "state_vector",
    "latent_tension",
    "causal_mirror",
    "laetitia_index",
    "scm_handoff",
    "continuity_event",
    "source_event_type",
    "source_module",
]


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    for key in REQUIRED_TOP_LEVEL_FIELDS:
        if key not in payload:
            errors.append(f"missing_top_level_field:{key}")

    state_vector = payload.get("state_vector") or {}
    if "state_vector_type" not in state_vector:
        errors.append("missing_state_vector_type")

    causal_mirror = payload.get("causal_mirror") or {}
    if "predicted_power_delta" not in causal_mirror:
        errors.append("missing_predicted_power_delta")

    laetitia_index = payload.get("laetitia_index") or {}
    if "total" not in laetitia_index:
        errors.append("missing_laetitia_total")

    scm_handoff = payload.get("scm_handoff") or {}
    continuity_event = payload.get("continuity_event") or {}
    if not scm_handoff and not continuity_event:
        errors.append("missing_scm_handoff_and_continuity_event")

    return errors


def append_manifest(entry: Dict[str, Any]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def copy_to_inbox(src: Path) -> Path:
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    dst = INBOX_DIR / src.name
    shutil.copy2(src, dst)
    return dst


def move_to_imported(src: Path) -> Path:
    IMPORTED_DIR.mkdir(parents=True, exist_ok=True)
    dst = IMPORTED_DIR / src.name
    shutil.move(str(src), str(dst))
    return dst


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    IMPORTED_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(SOURCE_DIR.glob("scm_*.json"))

    imported = 0
    skipped = 0

    for src in files:
        try:
            payload = load_json(src)
            errors = validate_payload(payload)

            inbox_copy = copy_to_inbox(src)

            manifest_entry = {
                "timestamp": datetime.now().isoformat(),
                "source_path": str(src),
                "inbox_copy": str(inbox_copy),
                "operator_id": payload.get("operator_id"),
                "session_id": payload.get("session_id"),
                "state_vector_type": (payload.get("state_vector") or {}).get("state_vector_type"),
                "continuity_event_type": (payload.get("continuity_event") or {}).get("event_type"),
                "valid": len(errors) == 0,
                "errors": errors,
            }
            append_manifest(manifest_entry)

            move_to_imported(src)

            if errors:
                skipped += 1
            else:
                imported += 1

        except Exception as exc:
            append_manifest(
                {
                    "timestamp": datetime.now().isoformat(),
                    "source_path": str(src),
                    "valid": False,
                    "errors": [f"exception:{str(exc)}"],
                }
            )
            skipped += 1

    print(
        json.dumps(
            {
                "scanned": len(files),
                "imported_valid": imported,
                "imported_with_errors": skipped,
                "source_dir": str(SOURCE_DIR),
                "inbox_dir": str(INBOX_DIR),
                "imported_dir": str(IMPORTED_DIR),
                "manifest_path": str(MANIFEST_PATH),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
