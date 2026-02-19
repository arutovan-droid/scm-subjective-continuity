"""
Sleep Consolidator - runs during low activity periods
Consolidates episodic scars into semantic clusters and archetypes
"""

import hashlib
import uuid
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity

from .memory_levels import HierarchicalMemory, EpisodicScar, SemanticCluster, Archetype


class SleepConsolidator:
    """
    Consolidates memories during sleep cycles.
    
    Three phases:
    1. Cluster episodic scars into semantic clusters
    2. Promote frequent semantic clusters to archetypes
    3. Archive consolidated episodic scars
    """
    
    def __init__(
        self,
        eps: float = 0.3,  # DBSCAN epsilon (cosine distance)
        min_samples: int = 3,  # Min scars to form a cluster
        archetype_threshold: int = 5,  # Min clusters to form an archetype
        similarity_threshold: float = 0.85  # Cosine similarity for archetype promotion
    ):
        self.eps = eps
        self.min_samples = min_samples
        self.archetype_threshold = archetype_threshold
        self.similarity_threshold = similarity_threshold
        
    async def consolidate(
        self,
        memory: HierarchicalMemory,
        max_age_hours: float = 72
    ) -> Tuple[List[SemanticCluster], List[str]]:
        """
        Run consolidation cycle.
        Returns: (new_clusters, archived_scar_ids)
        """
        # 1. Get old episodic scars
        old_scars = memory.get_episodic_for_consolidation(max_age_hours)
        if len(old_scars) < self.min_samples:
            return [], []
        
        # 2. Cluster embeddings
        embeddings = np.array([s.embedding for s in old_scars])
        clustering = DBSCAN(
            eps=self.eps,
            min_samples=self.min_samples,
            metric='cosine'
        ).fit(embeddings)
        
        # 3. Create semantic clusters
        new_clusters = []
        archived_ids = []
        
        labels = clustering.labels_
        unique_labels = set(labels)
        
        for label in unique_labels:
            if label == -1:  # noise - keep as episodic
                continue
                
            # Get scars in this cluster
            cluster_indices = np.where(labels == label)[0]
            cluster_scars = [old_scars[i] for i in cluster_indices]
            
            # Create semantic cluster
            cluster = self._create_semantic_cluster(cluster_scars)
            new_clusters.append(cluster)
            
            # Mark scars for archiving
            archived_ids.extend([s.scar_id for s in cluster_scars])
        
        # 4. Check for archetype promotion
        if new_clusters:
            await self._promote_to_archetypes(memory, new_clusters)
        
        return new_clusters, archived_ids
    
    def _create_semantic_cluster(self, scars: List[EpisodicScar]) -> SemanticCluster:
        """Create a semantic cluster from a list of scars"""
        # Compute centroid (mean of embeddings)
        embeddings = np.array([s.embedding for s in scars])
        centroid = np.mean(embeddings, axis=0)
        
        # Normalize centroid
        centroid = centroid / np.linalg.norm(centroid)
        
        # Compute statistics
        avg_entropy = np.mean([s.entropy_score for s in scars])
        avg_drift = np.mean([s.ontological_drift for s in scars])
        
        # Find dominant basis and type
        bases = [s.cognitive_basis for s in scars]
        types = [s.incident_type for s in scars]
        dominant_basis = max(set(bases), key=bases.count)
        dominant_type = max(set(types), key=types.count)
        
        # Create cluster ID from hashes
        source_hashes = [s.scar_hash for s in scars]
        source_ids = [s.scar_id for s in scars]
        hash_input = ''.join(sorted(source_hashes)).encode()
        cluster_id = hashlib.sha256(hash_input).hexdigest()[:16]
        
        # Compute proof hash (ZK-proof would go here in production)
        proof_input = f"{cluster_id}:{len(scars)}:{avg_entropy}".encode()
        proof_hash = hashlib.sha256(proof_input).hexdigest()
        
        return SemanticCluster(
            cluster_id=cluster_id,
            centroid=centroid,
            source_hashes=source_hashes,
            source_scar_ids=source_ids,
            avg_entropy=avg_entropy,
            avg_drift=avg_drift,
            dominant_basis=dominant_basis,
            dominant_type=dominant_type,
            count=len(scars),
            proof_hash=proof_hash
        )
    
    async def _promote_to_archetypes(
        self,
        memory: HierarchicalMemory,
        new_clusters: List[SemanticCluster]
    ):
        """Promote clusters to archetypes if they match existing patterns"""
        # Group clusters by dominant type/basis
        from collections import defaultdict
        
        type_groups = defaultdict(list)
        for cluster in new_clusters:
            key = f"{cluster.dominant_type}:{cluster.dominant_basis}"
            type_groups[key].append(cluster)
        
        # Check each group for promotion
        for key, clusters in type_groups.items():
            if len(clusters) < self.archetype_threshold:
                continue
            
            # Check if these clusters are similar to each other
            embeddings = np.array([c.centroid for c in clusters])
            sim_matrix = cosine_similarity(embeddings)
            
            # If all are highly similar, promote to archetype
            if np.all(sim_matrix > self.similarity_threshold):
                archetype = self._create_archetype(clusters, key)
                memory.add_archetype(archetype)
    
    def _create_archetype(self, clusters: List[SemanticCluster], key: str) -> Archetype:
        """Create an archetype from a group of similar clusters"""
        # Compute archetype embedding (mean of cluster centroids)
        embeddings = np.array([c.centroid for c in clusters])
        archetype_embedding = np.mean(embeddings, axis=0)
        archetype_embedding = archetype_embedding / np.linalg.norm(archetype_embedding)
        
        # Count total scars behind
        total_scars = sum(c.count for c in clusters)
        
        # Generate label
        incident_type, basis = key.split(':')
        label = f"{incident_type}_in_{basis}_becomes_archetype"
        
        # Compute weight based on cluster counts
        weight = min(1.0, total_scars / 50)  # 50 scars = full weight
        
        return Archetype(
            archetype_id=hashlib.sha256(key.encode()).hexdigest()[:16],
            label=label,
            embedding=archetype_embedding,
            weight=weight,
            source_clusters=[c.cluster_id for c in clusters],
            total_scars_behind=total_scars
        )
