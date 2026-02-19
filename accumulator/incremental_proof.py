"""
Incremental proofs for chain of scars.
"""

import hashlib
from typing import List, Optional
from accumulator.rsa_accumulator import RSAAccumulator, AccumulatorProof


class IncrementalChainProof:
    """
    Incremental proof for the entire chain of scars.
    Allows adding new scars without recomputing the entire chain.
    """
    
    def __init__(self, genesis_hash: bytes, wal_path: str = "chain.wal"):
        self.accumulator = RSAAccumulator(wal_path=wal_path)
        self.genesis = genesis_hash
        self.proofs: List[AccumulatorProof] = []
        
    async def initialize(self):
        """Initialize accumulator."""
        await self.accumulator.initialize()
        
        # If accumulator is empty, add genesis
        if self.accumulator.value == self.accumulator.g:
            await self.accumulator.add(self.genesis)
        
    async def add_scar(self, scar_hash: bytes) -> AccumulatorProof:
        """Add scar and return proof."""
        value, proof = await self.accumulator.add(scar_hash)
        self.proofs.append(proof)
        return proof
        
    def verify_chain(self, latest_proof: Optional[AccumulatorProof] = None) -> bool:
        """
        Verify entire chain using latest proof.
        O(1) verification!
        """
        if latest_proof is None:
            if not self.proofs:
                return True
            latest_proof = self.proofs[-1]
        
        # Verify the latest proof
        if not self.accumulator.verify(latest_proof):
            return False
            
        # Also verify that accumulator value matches
        return latest_proof.accumulator == self.accumulator.value
        
    def get_state_proof(self) -> Optional[AccumulatorProof]:
        """Return proof of current state."""
        if not self.proofs:
            return None
        return self.proofs[-1]
        
    @property
    def accumulator_value(self) -> int:
        """Current accumulator value."""
        return self.accumulator.value
