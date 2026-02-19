"""
RSA Accumulator for incremental proofs of scar chain.
Based on: "Dynamic Universal Accumulators with DLP" (Boneh et al.)
"""

import hashlib
from dataclasses import dataclass
from typing import List, Optional, Tuple
import asyncio

# For real cryptography use pycryptodome or cryptography
from Crypto.PublicKey import RSA
from Crypto.Util import number

from storage.wal_accumulator import AccumulatorWAL


@dataclass(frozen=True)
class AccumulatorProof:
    """Membership proof in accumulator."""
    witness: int
    accumulator: int
    element_hash: int
    sequence: int = 0


class RSAAccumulator:
    """
    RSA accumulator with support for:
    - Adding elements (O(1))
    - Removing elements (O(1)) with private key
    - Instant verification (O(1))
    - Incremental proofs
    """
    
    def __init__(self, key_size: int = 2048, wal_path: str = "accumulator.wal"):
        # Generate RSA modulus N = p * q
        # In production: generate in TEE, p and q destroyed after setup
        key = RSA.generate(key_size)
        self.N = key.n
        self.phi = (key.p - 1) * (key.q - 1)
        self.g = 65537  # Fixed generator
        self.value = self.g
        
        # Write-Ahead Log for recovery
        self.wal = AccumulatorWAL(wal_path)
        self.current_sequence = 0
        
    async def initialize(self):
        """Initialize from WAL on startup."""
        await self.wal.initialize_cache()
        self.current_sequence = self.wal.current_seq
        self.value = self.wal.current_value or self.g
        
    def _hash_to_prime(self, data: bytes) -> int:
        """Hash data to a prime number."""
        h = hashlib.sha256(data).digest()
        candidate = int.from_bytes(h, byteorder='big')
        
        # Find next prime
        while not number.isPrime(candidate):
            candidate += 1
            
        return candidate
        
    async def add(self, element_hash: bytes) -> Tuple[int, AccumulatorProof]:
        """
        Add element to accumulator.
        Returns new accumulator value and proof.
        """
        prime = self._hash_to_prime(element_hash)
        old_acc = self.value
        
        # New accumulator value: A_new = A_old^prime mod N
        self.value = pow(self.value, prime, self.N)
        self.current_sequence += 1
        
        # Save to WAL
        await self.wal.append("ADD", self.value, element_hash.hex()[:8])
        
        # Witness is the old accumulator value
        proof = AccumulatorProof(
            witness=old_acc,
            accumulator=self.value,
            element_hash=prime,  # Use prime, not original hash!
            sequence=self.current_sequence
        )
        
        return self.value, proof
        
    def verify(self, proof: AccumulatorProof) -> bool:
        """
        Verify membership proof.
        witness^element ≡ accumulator (mod N)
        """
        try:
            # witness^element mod N should equal accumulator
            computed = pow(proof.witness, proof.element_hash, self.N)
            return computed == proof.accumulator
        except Exception as e:
            print(f"Verification error: {e}")
            return False
            
    def batch_verify(self, proofs: List[AccumulatorProof]) -> bool:
        """Batch verify multiple proofs."""
        return all(self.verify(p) for p in proofs)
        
    async def remove(self, element_hash: bytes) -> int:
        """
        Remove element (requires phi(N)).
        Used only for chain reorganization (rare).
        """
        prime = self._hash_to_prime(element_hash)
        
        # Find inverse modulo phi(N)
        inv = pow(prime, -1, self.phi)
        
        # new_value = accumulator^inv mod N
        self.value = pow(self.value, inv, self.N)
        self.current_sequence += 1
        
        await self.wal.append("REMOVE", self.value, element_hash.hex()[:8])
        return self.value
