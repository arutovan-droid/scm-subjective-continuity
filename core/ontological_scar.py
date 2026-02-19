"""
Ontological scar model — evidence of encounter.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
import uuid
import hashlib
from datetime import datetime

from accumulator.rsa_accumulator import AccumulatorProof


@dataclass(frozen=True)
class OntologicalScar:
    """
    Ontological trauma scar.
    Contains incremental proof of chain membership.
    """
    # Identification
    scar_id: uuid.UUID
    genesis_ref: str
    
    # Incident type
    incident_type: str  # 'rejection', 'betrayal', 'exhaustion', 'mimicry_detected'
    
    # Cognitive context
    cognitive_basis: str  # 'de', 'ru', 'hy', 'en', 'sa'
    collision_mode: bool
    pole_a: Optional[str] = None
    pole_b: Optional[str] = None
    
    # Structural data
    pre_state_hash: str
    post_state_hash: str
    deformation_vector: Dict[str, Any]
    
    # Proof
    chain_proof: Optional[AccumulatorProof] = None
    accumulator_value: Optional[int] = None
    
    # Metadata
    entropy_score: float
    ontological_drift: float
    timestamp: datetime
    operator_id: str
    
    def to_hash(self) -> bytes:
        """Scar hash for accumulator."""
        content = f"{self.scar_id}{self.pre_state_hash}{self.post_state_hash}{self.timestamp}"
        return hashlib.sha256(content.encode()).digest()
