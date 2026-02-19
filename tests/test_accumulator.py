"""
Tests for RSA accumulator.
"""

import pytest
import pytest_asyncio
import hashlib
import tempfile
import os

from accumulator.rsa_accumulator import RSAAccumulator
from accumulator.incremental_proof import IncrementalChainProof


@pytest_asyncio.fixture
async def accumulator():
    """Create accumulator for tests."""
    with tempfile.NamedTemporaryFile(suffix='.wal', delete=False) as f:
        wal_path = f.name
    
    acc = RSAAccumulator(key_size=1024, wal_path=wal_path)
    await acc.initialize()
    yield acc
    
    # Cleanup
    os.unlink(wal_path)


@pytest.mark.asyncio
async def test_add_and_verify(accumulator):
    """Test add and verify."""
    element = hashlib.sha256(b"test_element").digest()
    new_value, proof = await accumulator.add(element)
    
    # Verify the proof
    assert accumulator.verify(proof) == True
    
    # Verify that accumulator value matches
    assert new_value == accumulator.value


@pytest.mark.asyncio
async def test_batch_verify(accumulator):
    """Test batch verification."""
    proofs = []
    for i in range(10):
        element = hashlib.sha256(f"element_{i}".encode()).digest()
        value, proof = await accumulator.add(element)
        proofs.append(proof)
        
    # Verify all proofs
    for proof in proofs:
        assert accumulator.verify(proof) == True


@pytest.mark.asyncio
async def test_incremental_chain():
    """Test incremental chain."""
    with tempfile.NamedTemporaryFile(suffix='.wal', delete=False) as f:
        wal_path = f.name
    
    chain = IncrementalChainProof(
        genesis_hash=hashlib.sha256(b"genesis").digest(),
        wal_path=wal_path
    )
    await chain.initialize()
    
    # Add 10 scars (reduced from 100 for speed)
    for i in range(10):
        scar_hash = hashlib.sha256(f"scar_{i}".encode()).digest()
        proof = await chain.add_scar(scar_hash)
        
        # Verify the proof directly
        assert chain.accumulator.verify(proof) == True
        
        # Verify the whole chain
        assert chain.verify_chain() == True
    
    # Final verification
    assert chain.verify_chain() == True
    assert len(chain.proofs) == 10
        
    os.unlink(wal_path)
