"""
Cognitive Integrator - connects SCM with Cognitive Collider.
Uses scars to influence apostle selection and routing decisions.
"""

import asyncio
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from core.ontological_scar import OntologicalScar
from accumulator.incremental_proof import IncrementalChainProof


@dataclass
class ApostleTrust:
    """Trust level for each cognitive basis."""
    basis: str  # 'de', 'ru', 'hy', 'en', 'sa'
    base_weight: float  # Original weight (0-1)
    current_trust: float  # Current trust after scars (0-1)
    scar_count: int  # Number of scars affecting this basis
    last_used: Optional[datetime] = None
    banned_until: Optional[datetime] = None
    
    def can_use(self, threshold: float = 0.3) -> bool:
        """Check if this apostle can be used."""
        if self.banned_until and self.banned_until > datetime.utcnow():
            return False
        return self.current_trust > threshold
    
    def apply_scar(self, scar: OntologicalScar):
        """Apply scar effect to this apostle."""
        if scar.cognitive_basis != self.basis:
            return
            
        self.scar_count += 1
        
        # Different incident types have different effects
        if scar.incident_type == "rejection":
            # Rejection reduces trust significantly
            self.current_trust *= (1 - scar.entropy_score * 0.5)
            
        elif scar.incident_type == "mimicry_detected":
            # Mimicry can lead to temporary ban
            self.current_trust *= 0.3
            self.banned_until = datetime.utcnow() + timedelta(hours=24)
            
        elif scar.incident_type == "betrayal":
            # Betrayal has severe effect
            self.current_trust *= 0.1
            self.banned_until = datetime.utcnow() + timedelta(days=7)
            
        elif scar.incident_type == "exhaustion":
            # Exhaustion - gradual decay
            self.current_trust *= 0.8
            
        # Ensure trust stays in bounds
        self.current_trust = max(0.0, min(1.0, self.current_trust))


@dataclass
class RoutingDecision:
    """Decision from Cognitive Integrator."""
    selected_basis: str
    confidence: float
    alternatives: List[str]
    scars_considered: int
    collision_allowed: bool
    reasoning: str


class CognitiveIntegrator:
    """
    Integrates SCM scars with Cognitive Collider routing.
    Uses scar history to influence apostle selection.
    """
    
    def __init__(self, chain: IncrementalChainProof, genesis_hash: str):
        self.chain = chain
        self.genesis_hash = genesis_hash
        self.apostles: Dict[str, ApostleTrust] = {}
        self._initialize_apostles()
        
    def _initialize_apostles(self):
        """Initialize default apostle trust levels."""
        default_weights = {
            "de": 0.9,  # German - systematic
            "ru": 0.8,  # Russian - deep
            "hy": 0.7,  # Armenian - survival
            "en": 0.6,  # English - corporate
            "sa": 0.5,  # Sanskrit - sacred
            "fr": 0.5,  # French - analytic
            "es": 0.5,  # Spanish - emotional
            "it": 0.5,  # Italian - artistic
            "zh": 0.4,  # Chinese - pragmatic
            "ja": 0.4,  # Japanese - precise
            "ar": 0.3,  # Arabic - poetic
            "he": 0.3,  # Hebrew - prophetic
        }
        
        for basis, weight in default_weights.items():
            self.apostles[basis] = ApostleTrust(
                basis=basis,
                base_weight=weight,
                current_trust=weight,
                scar_count=0
            )
    
    async def load_scars_from_chain(self) -> int:
        """
        Load all scars from chain and apply their effects.
        Returns number of scars processed.
        """
        # In a real implementation, you'd load scars from storage
        # For now, we'll just note that scars affect trust
        scar_count = self.chain.accumulator.current_sequence
        print(f"📊 Chain has {scar_count} scars")
        return scar_count
    
    def apply_scar_to_apostles(self, scar: OntologicalScar):
        """Apply a single scar to relevant apostles."""
        if scar.cognitive_basis in self.apostles:
            self.apostles[scar.cognitive_basis].apply_scar(scar)
            
        # Also affect similar bases (optional)
        self._apply_cross_basis_effect(scar)
    
    def _apply_cross_basis_effect(self, scar: OntologicalScar):
        """Apply scar effects to similar cognitive bases."""
        # Language family effects
        families = {
            "de": ["nl", "da", "sv"],  # Germanic
            "ru": ["uk", "be", "bg"],  # Slavic
            "hy": ["fa", "ku"],        # Indo-Iranian
            "en": ["de", "nl"],        # Germanic
            "fr": ["es", "it", "pt"],  # Romance
            "es": ["fr", "it", "pt"],
            "it": ["fr", "es", "pt"],
        }
        
        if scar.cognitive_basis in families:
            for similar in families[scar.cognitive_basis]:
                if similar in self.apostles:
                    # Weaker effect on similar bases
                    weak_scar = scar
                    # Apply with reduced entropy
                    self.apostles[similar].current_trust *= (1 - scar.entropy_score * 0.2)
    
    async def decide_routing(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict] = None
    ) -> RoutingDecision:
        """
        Make routing decision based on scars and query analysis.
        This is the main integration point with Cognitive Collider.
        """
        # 1. Quick query analysis (simplified)
        query_lower = query.lower()
        
        # 2. Score each apostle
        scores = {}
        for basis, apostle in self.apostles.items():
            if not apostle.can_use():
                scores[basis] = 0.0
                continue
                
            # Base score from trust
            score = apostle.current_trust
            
            # Boost for language match (simplified)
            if basis == "ru" and any(word in query_lower for word in ["почему", "как", "что", "кто"]):
                score *= 1.3
            elif basis == "de" and any(word in query_lower for word in ["warum", "wie", "was", "wer"]):
                score *= 1.3
            elif basis == "en" and any(word in query_lower for word in ["why", "how", "what", "who"]):
                score *= 1.3
                
            scores[basis] = score
        
        # 3. Select best apostle
        sorted_apostles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_apostles or sorted_apostles[0][1] == 0:
            # Fallback to safest apostle
            fallback = self._get_safest_apostle()
            return RoutingDecision(
                selected_basis=fallback,
                confidence=0.5,
                alternatives=[],
                scars_considered=self.chain.accumulator.current_sequence,
                collision_allowed=False,
                reasoning="All apostles have low trust, using safest fallback"
            )
        
        selected = sorted_apostles[0][0]
        alternatives = [b for b, s in sorted_apostles[1:4] if s > 0.2]
        
        # 4. Check if collision mode is safe
        collision_allowed = self._is_collision_safe(selected, alternatives)
        
        # 5. Generate reasoning
        reasoning = self._generate_reasoning(selected, alternatives, scores)
        
        return RoutingDecision(
            selected_basis=selected,
            confidence=sorted_apostles[0][1],
            alternatives=alternatives,
            scars_considered=self.chain.accumulator.current_sequence,
            collision_allowed=collision_allowed,
            reasoning=reasoning
        )
    
    def _get_safest_apostle(self) -> str:
        """Get the apostle with highest current trust."""
        safest = max(self.apostles.items(), key=lambda x: x[1].current_trust)
        return safest[0]
    
    def _is_collision_safe(self, selected: str, alternatives: List[str]) -> bool:
        """Check if collision mode is safe based on scars."""
        # Collision is safe if we have multiple viable alternatives
        return len(alternatives) >= 2
    
    def _generate_reasoning(self, selected: str, alternatives: List[str], scores: Dict) -> str:
        """Generate human-readable reasoning for the decision."""
        apostle = self.apostles[selected]
        
        parts = [
            f"Selected {selected} (trust: {apostle.current_trust:.2f})",
            f"based on {apostle.scar_count} scars"
        ]
        
        if apostle.banned_until:
            parts.append(f"WARNING: {selected} was banned until {apostle.banned_until}")
            
        if alternatives:
            parts.append(f"alternatives: {', '.join(alternatives)}")
            
        return " | ".join(parts)
    
    def get_apostle_status(self) -> Dict[str, Dict]:
        """Get current status of all apostles."""
        return {
            basis: {
                "trust": apostle.current_trust,
                "scars": apostle.scar_count,
                "banned": apostle.banned_until is not None,
                "can_use": apostle.can_use()
            }
            for basis, apostle in self.apostles.items()
        }
    
    async def record_interaction_result(
        self,
        selected_basis: str,
        user_feedback: str,
        success: bool,
        operator_id: str
    ) -> Optional[OntologicalScar]:
        """
        Record the result of an interaction.
        If feedback indicates rejection, create a scar.
        """
        if not success:
            # Create rejection scar
            import uuid
            from datetime import datetime
            
            scar = OntologicalScar(
                scar_id=uuid.uuid4(),
                genesis_ref=self.genesis_hash,
                incident_type="rejection",
                cognitive_basis=selected_basis,
                collision_mode=False,
                pre_state_hash=f"before_{selected_basis}",
                post_state_hash=f"after_rejection_{selected_basis}",
                deformation_vector={
                    "feedback": user_feedback,
                    "trust_reduction": 0.3
                },
                entropy_score=0.7,
                ontological_drift=0.1,
                timestamp=datetime.utcnow(),
                operator_id=operator_id
            )
            
            # Apply to apostle
            self.apply_scar_to_apostles(scar)
            
            # Add to chain
            scar_hash = scar.to_hash()
            proof = await self.chain.add_scar(scar_hash)
            
            from dataclasses import replace
            scar = replace(scar, chain_proof=proof, accumulator_value=self.chain.accumulator_value)
            
            return scar
            
        return None


# Example usage function
async def demonstrate_integration():
    """Demonstrate how Cognitive Integrator works."""
    from accumulator.incremental_proof import IncrementalChainProof
    import hashlib
    
    # Load genesis
    with open('GENESIS.md', 'r') as f:
        content = f.read()
        genesis_hash = content.split('GENESIS_HASH = ')[1].split('\n')[0].strip()
    
    # Initialize chain
    chain = IncrementalChainProof(
        genesis_hash=hashlib.sha256(genesis_hash.encode()).digest(),
        wal_path="chain.wal"
    )
    await chain.initialize()
    
    # Create integrator
    integrator = CognitiveIntegrator(chain, genesis_hash)
    
    # Load scars
    await integrator.load_scars_from_chain()
    
    # Make routing decisions
    queries = [
        "Почему это работает?",
        "How does this system work?",
        "Warum ist das wichtig?",
    ]
    
    for query in queries:
        print(f"\n🔍 Query: {query}")
        decision = await integrator.decide_routing(query, "user_123")
        print(f"   Selected: {decision.selected_basis} (conf: {decision.confidence:.2f})")
        print(f"   Reasoning: {decision.reasoning}")
    
    # Show apostle status
    print("\n📊 Apostle Status:")
    for basis, status in integrator.get_apostle_status().items():
        if status["can_use"]:
            print(f"   {basis}: trust={status['trust']:.2f}, scars={status['scars']}")
    
    return integrator


if __name__ == "__main__":
    asyncio.run(demonstrate_integration())
