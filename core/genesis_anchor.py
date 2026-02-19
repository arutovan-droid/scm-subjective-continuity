"""
Genesis Anchor — system birth point.
Fixed once at first run in TEE.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GenesisAnchor:
    """System genesis anchor."""
    hash: str
    timestamp: str
    attestation: Optional[str] = None
    sealed_in_tee: bool = True
    
    def __post_init__(self):
        if self.sealed_in_tee and not self.attestation:
            object.__setattr__(self, 'attestation', 'TEE_SEALED')
