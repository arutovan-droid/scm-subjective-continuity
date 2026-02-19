"""
Hierarchical Memory System for SCM v2.0
Three levels: Episodic (short-term), Semantic (long-term), Archetypal (core beliefs)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
import numpy as np
import json


class MemoryLevel(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    ARCHETYPAL = "archetypal"


@dataclass
class EpisodicScar:
    """
    Fresh scar with full details.
    Lives for 24-72 hours before consolidation.
    """
    scar_id: str
    scar_hash: str
    incident_type: str
    cognitive_basis: str
    entropy_score: float
    ontological_drift: float
    deformation_vector: Dict[str, Any]
    embedding: np.ndarray  # dim=128
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    # For chain integrity
    pre_state_hash: Optional[str] = None
    post_state_hash: Optional[str] = None
    accumulator_value: Optional[int] = None
    witness_proof: Optional[Dict] = None
    
    @property
    def age_hours(self) -> float:
        """Age in hours"""
        return (datetime.utcnow() - self.created_at).total_seconds() / 3600
    
    @property
    def salience(self) -> float:
        """
        Salience = entropy * drift * recency * access_boost
        Higher salience means more likely to be remembered
        """
        base = self.entropy_score * abs(self.ontological_drift)
        
        # Recency factor: decays over 7 days (168 hours)
        recency = max(0.1, 1.0 - self.age_hours / 168)
        
        # Access boost: each access increases salience by 10%
        access_boost = 1.0 + 0.1 * self.access_count
        
        return base * recency * access_boost
    
    def to_dict(self) -> Dict:
        """Convert to dict for storage"""
        return {
            "scar_id": self.scar_id,
            "scar_hash": self.scar_hash,
            "incident_type": self.incident_type,
            "cognitive_basis": self.cognitive_basis,
            "entropy_score": self.entropy_score,
            "ontological_drift": self.ontological_drift,
            "deformation_vector": self.deformation_vector,
            "embedding": self.embedding.tolist(),
            "created_at": self.created_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "pre_state_hash": self.pre_state_hash,
            "post_state_hash": self.post_state_hash,
            "accumulator_value": self.accumulator_value,
            "witness_proof": self.witness_proof
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "EpisodicScar":
        """Create from dict"""
        data["embedding"] = np.array(data["embedding"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("last_accessed"):
            data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
        return cls(**data)


@dataclass
class SemanticCluster:
    """
    Generalized pattern from multiple episodic scars.
    Lives forever, but can be updated.
    """
    cluster_id: str
    centroid: np.ndarray  # dim=128
    source_hashes: List[str]  # scar_hashes that formed this cluster
    source_scar_ids: List[str]
    
    # Statistical summary
    avg_entropy: float
    avg_drift: float
    dominant_basis: str
    dominant_type: str
    count: int
    
    # Metadata
    consolidated_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    
    # For chain integrity (ZK-proof of aggregation)
    proof_hash: Optional[str] = None
    
    @property
    def confidence(self) -> float:
        """Confidence in this cluster (0-1)"""
        return min(1.0, self.count / 10)  # 10 scars = full confidence
    
    def to_dict(self) -> Dict:
        """Convert to dict for storage"""
        return {
            "cluster_id": self.cluster_id,
            "centroid": self.centroid.tolist(),
            "source_hashes": self.source_hashes,
            "source_scar_ids": self.source_scar_ids,
            "avg_entropy": self.avg_entropy,
            "avg_drift": self.avg_drift,
            "dominant_basis": self.dominant_basis,
            "dominant_type": self.dominant_type,
            "count": self.count,
            "consolidated_at": self.consolidated_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "access_count": self.access_count,
            "proof_hash": self.proof_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SemanticCluster":
        """Create from dict"""
        data["centroid"] = np.array(data["centroid"])
        data["consolidated_at"] = datetime.fromisoformat(data["consolidated_at"])
        if data.get("last_accessed"):
            data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
        return cls(**data)


@dataclass
class Archetype:
    """
    Deep belief formed from multiple semantic clusters.
    Immutable once formed.
    """
    archetype_id: str
    label: str  # e.g., "operators_never_trust_de_after_rejection"
    embedding: np.ndarray  # dim=128
    weight: float  # 0..1, how strongly this influences decisions
    
    # Sources
    source_clusters: List[str]  # cluster_ids
    total_scars_behind: int
    
    # Metadata
    formed_at: datetime = field(default_factory=datetime.utcnow)
    immutable: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dict for storage"""
        return {
            "archetype_id": self.archetype_id,
            "label": self.label,
            "embedding": self.embedding.tolist(),
            "weight": self.weight,
            "source_clusters": self.source_clusters,
            "total_scars_behind": self.total_scars_behind,
            "formed_at": self.formed_at.isoformat(),
            "immutable": self.immutable
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Archetype":
        """Create from dict"""
        data["embedding"] = np.array(data["embedding"])
        data["formed_at"] = datetime.fromisoformat(data["formed_at"])
        return cls(**data)


class HierarchicalMemory:
    """
    Main memory manager for SCM v2.0.
    Handles three levels of memory with automatic consolidation.
    """
    
    def __init__(self, storage_path: str = "memory.db"):
        self.storage_path = storage_path
        
        # Three memory levels
        self.episodic: Dict[str, EpisodicScar] = {}  # scar_id -> scar
        self.semantic: Dict[str, SemanticCluster] = {}  # cluster_id -> cluster
        self.archetypes: Dict[str, Archetype] = {}  # archetype_id -> archetype
        
        # Indexes
        self.basis_index: Dict[str, List[str]] = {}  # cognitive_basis -> [scar_ids]
        self.type_index: Dict[str, List[str]] = {}  # incident_type -> [scar_ids]
        
    def add_episodic(self, scar: EpisodicScar):
        """Add a new episodic scar"""
        self.episodic[scar.scar_id] = scar
        
        # Update indexes
        self.basis_index.setdefault(scar.cognitive_basis, []).append(scar.scar_id)
        self.type_index.setdefault(scar.incident_type, []).append(scar.scar_id)
        
    def get_episodic_for_consolidation(self, max_age_hours: float = 72) -> List[EpisodicScar]:
        """Get episodic scars older than max_age_hours for consolidation"""
        now = datetime.utcnow()
        return [
            scar for scar in self.episodic.values()
            if (now - scar.created_at).total_seconds() / 3600 > max_age_hours
        ]
    
    def add_semantic(self, cluster: SemanticCluster):
        """Add a new semantic cluster"""
        self.semantic[cluster.cluster_id] = cluster
        
    def add_archetype(self, archetype: Archetype):
        """Add a new archetype"""
        self.archetypes[archetype.archetype_id] = archetype
        
    def find_similar_semantic(self, embedding: np.ndarray, threshold: float = 0.8) -> List[SemanticCluster]:
        """Find semantic clusters similar to given embedding"""
        from sklearn.metrics.pairwise import cosine_similarity
        
        results = []
        for cluster in self.semantic.values():
            sim = cosine_similarity([embedding], [cluster.centroid])[0][0]
            if sim > threshold:
                results.append((sim, cluster))
        
        results.sort(reverse=True)
        return [r[1] for r in results]
    
    def get_by_basis(self, basis: str, level: MemoryLevel = MemoryLevel.EPISODIC) -> List:
        """Get memories by cognitive basis"""
        if level == MemoryLevel.EPISODIC:
            scar_ids = self.basis_index.get(basis, [])
            return [self.episodic[sid] for sid in scar_ids if sid in self.episodic]
        elif level == MemoryLevel.SEMANTIC:
            return [c for c in self.semantic.values() if c.dominant_basis == basis]
        else:  # ARCHETYPAL
            return [a for a in self.archetypes.values()]  # archetypes aren't basis-specific
    
    def save(self):
        """Save memory to disk"""
        import pickle
        
        data = {
            "episodic": {k: v.to_dict() for k, v in self.episodic.items()},
            "semantic": {k: v.to_dict() for k, v in self.semantic.items()},
            "archetypes": {k: v.to_dict() for k, v in self.archetypes.items()},
            "basis_index": self.basis_index,
            "type_index": self.type_index
        }
        
        with open(self.storage_path, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self):
        """Load memory from disk"""
        import pickle
        import os
        
        if not os.path.exists(self.storage_path):
            return
        
        with open(self.storage_path, 'rb') as f:
            data = pickle.load(f)
        
        self.episodic = {k: EpisodicScar.from_dict(v) for k, v in data["episodic"].items()}
        self.semantic = {k: SemanticCluster.from_dict(v) for k, v in data["semantic"].items()}
        self.archetypes = {k: Archetype.from_dict(v) for k, v in data["archetypes"].items()}
        self.basis_index = data["basis_index"]
        self.type_index = data["type_index"]
