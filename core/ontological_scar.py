"""
Ontological scar model — evidence of encounter.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
import uuid
import hashlib
from datetime import datetime

from accumulator.rsa_accumulator import AccumulatorProof


@dataclass
class OntologicalScar:
    """
    Ontological trauma scar.
    Contains incremental proof of chain membership.
    """
    # Required fields (no defaults)
    scar_id: uuid.UUID
    genesis_ref: str
    incident_type: str
    cognitive_basis: str
    collision_mode: bool
    pre_state_hash: str
    post_state_hash: str
    deformation_vector: Dict[str, Any]
    entropy_score: float
    ontological_drift: float
    timestamp: datetime
    operator_id: str
    
    # Optional fields (with defaults)
    pole_a: Optional[str] = None
    pole_b: Optional[str] = None
    chain_proof: Optional[AccumulatorProof] = None
    accumulator_value: Optional[int] = None
    
    def to_hash(self) -> bytes:
        """Scar hash for accumulator."""
        content = f"{self.scar_id}{self.pre_state_hash}{self.post_state_hash}{self.timestamp}"
        return hashlib.sha256(content.encode()).digest()
