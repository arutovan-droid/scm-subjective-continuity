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
    
    assert accumulator.verify(proof) == True


@pytest.mark.asyncio
async def test_batch_verify(accumulator):
    """Test batch verification."""
    proofs = []
    for i in range(10):
        element = hashlib.sha256(f"element_{i}".encode()).digest()
        _, proof = await accumulator.add(element)
        proofs.append(proof)
        
    assert accumulator.batch_verify(proofs) == True


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
    
    # Add 100 scars
    for i in range(100):
        scar_hash = hashlib.sha256(f"scar_{i}".encode()).digest()
        proof = await chain.add_scar(scar_hash)
        
        # Verify after each add
        assert chain.verify_chain(proof) == True
        
    os.unlink(wal_path)
