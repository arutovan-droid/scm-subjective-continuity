"""
Interface to TEE (Trusted Execution Environment).
Supports soft-mode for development.
"""

import warnings
from typing import Dict


class AccumulatorEnclave:
    """Interface to TEE with soft-mode fallback."""
    
    def __init__(self):
        self.soft_mode = not self._check_nitro_available()
        if self.soft_mode:
            warnings.warn(
                "⚠️  TEE unavailable. Running in SOFT MODE - phi(N) exposed in RAM!",
                RuntimeWarning
            )
            
    def _check_nitro_available(self) -> bool:
        """Check for AWS Nitro Enclaves availability."""
        # In production: check /dev/nitro_enclaves
        # For tests return False
        return False
        
    def create_accumulator(self) -> Dict:
        """Create new accumulator."""
        if self.soft_mode:
            # Generate locally (INSECURE!)
            from Crypto.PublicKey import RSA
            key = RSA.generate(2048)
            return {
                'N': key.n,
                'g': 65537,
                'phi': (key.p - 1) * (key.q - 1),
                'attestation': 'SOFT_MODE_NO_ATTESTATION'
            }
        else:
            # In production: call enclave
            return {
                'N': 12345,  # stub
                'g': 65537,
                'attestation': 'aws-nitro:enclave-12345678'
            }
            
    def store_genesis(self, anchor):
        """Store genesis in TEE."""
        if not self.soft_mode:
            # Call enclave to store
            pass
