"""
Tests for Hierarchical Memory (Extension 1)
"""

import pytest
import asyncio
import numpy as np
import uuid
from datetime import datetime, timedelta

from core.liveness_v2.memory_levels import (
    EpisodicScar, SemanticCluster, Archetype, HierarchicalMemory
)
from core.liveness_v2.sleep_consolidator import SleepConsolidator


@pytest.fixture
def sample_episodic_scar():
    """Create a sample episodic scar for testing"""
    return EpisodicScar(
        scar_id=str(uuid.uuid4()),
        scar_hash="test_hash_123",
        incident_type="rejection",
        cognitive_basis="ru",
        entropy_score=0.8,
        ontological_drift=0.2,
        deformation_vector={"reason": "test"},
        embedding=np.random.randn(128),
        created_at=datetime.utcnow() - timedelta(days=3)
    )


@pytest.fixture
def fresh_episodic_scar():
    """Create a fresh episodic scar"""
    return EpisodicScar(
        scar_id=str(uuid.uuid4()),
        scar_hash="test_hash_456",
        incident_type="rejection",
        cognitive_basis="ru",
        entropy_score=0.8,
        ontological_drift=0.2,
        deformation_vector={"reason": "test"},
        embedding=np.random.randn(128),
        created_at=datetime.utcnow()
    )


def test_episodic_salience(sample_episodic_scar, fresh_episodic_scar):
    """Test that salience decays with age"""
    # Old scar should have lower salience
    assert sample_episodic_scar.salience < fresh_episodic_scar.salience
    
    # Access should increase salience
    old_val = sample_episodic_scar.salience
    sample_episodic_scar.access_count += 1
    assert sample_episodic_scar.salience > old_val


def test_episodic_ttl():
    """Test that scars older than threshold are marked for consolidation"""
    memory = HierarchicalMemory(":memory:")
    
    # Add old scars
    old_scars = []
    for i in range(5):
        scar = EpisodicScar(
            scar_id=str(uuid.uuid4()),
            scar_hash=f"old_{i}",
            incident_type="rejection",
            cognitive_basis="ru",
            entropy_score=0.8,
            ontological_drift=0.2,
            deformation_vector={},
            embedding=np.random.randn(128),
            created_at=datetime.utcnow() - timedelta(days=4)
        )
        memory.add_episodic(scar)
        old_scars.append(scar)
    
    # Add fresh scars
    for i in range(3):
        scar = EpisodicScar(
            scar_id=str(uuid.uuid4()),
            scar_hash=f"fresh_{i}",
            incident_type="rejection",
            cognitive_basis="ru",
            entropy_score=0.8,
            ontological_drift=0.2,
            deformation_vector={},
            embedding=np.random.randn(128),
            created_at=datetime.utcnow()
        )
        memory.add_episodic(scar)
    
    # Get old scars
    to_consolidate = memory.get_episodic_for_consolidation(max_age_hours=72)
    assert len(to_consolidate) == 5


@pytest.mark.asyncio
async def test_consolidation():
    """Test that 3+ similar scars consolidate into a semantic cluster"""
    memory = HierarchicalMemory(":memory:")
    consolidator = SleepConsolidator(min_samples=3)
    
    # Create 3 similar scars
    base_embedding = np.random.randn(128)
    base_embedding = base_embedding / np.linalg.norm(base_embedding)
    
    for i in range(3):
        # Add small noise to make them similar but not identical
        noise = np.random.randn(128) * 0.05
        embedding = base_embedding + noise
        embedding = embedding / np.linalg.norm(embedding)
        
        scar = EpisodicScar(
            scar_id=str(uuid.uuid4()),
            scar_hash=f"similar_{i}",
            incident_type="rejection",
            cognitive_basis="ru",
            entropy_score=0.8,
            ontological_drift=0.2,
            deformation_vector={},
            embedding=embedding,
            created_at=datetime.utcnow() - timedelta(days=4)
        )
        memory.add_episodic(scar)
    
    # Add a dissimilar scar (noise)
    scar = EpisodicScar(
        scar_id=str(uuid.uuid4()),
        scar_hash="dissimilar",
        incident_type="rejection",
        cognitive_basis="ru",
        entropy_score=0.8,
        ontological_drift=0.2,
        deformation_vector={},
        embedding=np.random.randn(128),
        created_at=datetime.utcnow() - timedelta(days=4)
    )
    memory.add_episodic(scar)
    
    # Consolidate
    new_clusters, archived = await consolidator.consolidate(memory)
    
    # Should have 1 cluster from the 3 similar scars
    assert len(new_clusters) == 1
    assert len(archived) == 3
    
    # Dissimilar scar should remain
    assert "dissimilar" not in archived


@pytest.mark.asyncio
async def test_archetype_promotion():
    """Test that 5+ clusters promote to archetype"""
    memory = HierarchicalMemory(":memory:")
    consolidator = SleepConsolidator(
        min_samples=3,
        archetype_threshold=5,
        similarity_threshold=0.85
    )
    
    # Create 5 clusters with similar centroids
    base_embedding = np.random.randn(128)
    base_embedding = base_embedding / np.linalg.norm(base_embedding)
    
    for cluster_idx in range(5):
        # Create 3 scars per cluster
        cluster_scars = []
        for i in range(3):
            noise = np.random.randn(128) * 0.02
            embedding = base_embedding + noise
            embedding = embedding / np.linalg.norm(embedding)
            
            scar = EpisodicScar(
                scar_id=str(uuid.uuid4()),
                scar_hash=f"c{cluster_idx}_s{i}",
                incident_type="rejection",
                cognitive_basis="ru",
                entropy_score=0.8,
                ontological_drift=0.2,
                deformation_vector={},
                embedding=embedding,
                created_at=datetime.utcnow() - timedelta(days=4)
            )
            memory.add_episodic(scar)
            cluster_scars.append(scar)
        
        # Create cluster from these scars (would normally happen in consolidation)
        cluster = consolidator._create_semantic_cluster(cluster_scars)
        memory.add_semantic(cluster)
    
    # Promote to archetypes
    await consolidator._promote_to_archetypes(memory, list(memory.semantic.values()))
    
    # Should have 1 archetype
    assert len(memory.archetypes) == 1


def test_chain_integrity_after_consolidation():
    """Test that chain remains valid after memory operations"""
    # This is a placeholder - actual test would need real chain
    assert True


def test_no_data_loss():
    """Test that source hashes are preserved in clusters"""
    memory = HierarchicalMemory(":memory:")
    
    # Create scars
    scar_ids = []
    for i in range(3):
        scar_id = str(uuid.uuid4())
        scar_ids.append(scar_id)
        scar = EpisodicScar(
            scar_id=scar_id,
            scar_hash=f"hash_{i}",
            incident_type="rejection",
            cognitive_basis="ru",
            entropy_score=0.8,
            ontological_drift=0.2,
            deformation_vector={},
            embedding=np.random.randn(128),
            created_at=datetime.utcnow()
        )
        memory.add_episodic(scar)
    
    # Create cluster manually
    consolidator = SleepConsolidator()
    cluster = consolidator._create_semantic_cluster(list(memory.episodic.values()))
    
    # Check that all source hashes are preserved
    assert set(cluster.source_scar_ids) == set(scar_ids)
