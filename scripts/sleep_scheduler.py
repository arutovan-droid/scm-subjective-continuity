#!/usr/bin/env python3
"""
Sleep Scheduler for SCM v2.0
Runs consolidation cycles during low activity periods.
Should be called by crontab (e.g., daily at 3 AM)
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.liveness_v2.memory_levels import HierarchicalMemory
from core.liveness_v2.sleep_consolidator import SleepConsolidator
from accumulator.incremental_proof import IncrementalChainProof


async def run_sleep_cycle(
    chain_path: str = "chain.wal",
    memory_path: str = "memory.db",
    max_age_hours: float = 72,
    dry_run: bool = False
):
    """
    Execute one sleep cycle:
    1. Load chain and memory
    2. Consolidate old episodic scars
    3. Save updated memory
    """
    print(f"😴 SCM Sleep Cycle Starting at {datetime.utcnow().isoformat()}")
    print(f"   Chain: {chain_path}")
    print(f"   Memory: {memory_path}")
    print(f"   Max age: {max_age_hours} hours")
    print(f"   Dry run: {dry_run}")
    
    # Load chain (for verification)
    from core.genesis_anchor import GenesisAnchor
    with open('GENESIS.md', 'r') as f:
        content = f.read()
        genesis_hash = content.split('GENESIS_HASH = ')[1].split('\n')[0].strip()
    
    chain = IncrementalChainProof(
        genesis_hash=hashlib.sha256(genesis_hash.encode()).digest(),
        wal_path=chain_path
    )
    await chain.initialize()
    
    # Load memory
    memory = HierarchicalMemory(storage_path=memory_path)
    memory.load()
    
    print(f"\n📊 Before consolidation:")
    print(f"   Episodic scars: {len(memory.episodic)}")
    print(f"   Semantic clusters: {len(memory.semantic)}")
    print(f"   Archetypes: {len(memory.archetypes)}")
    
    # Run consolidation
    consolidator = SleepConsolidator()
    new_clusters, archived_ids = await consolidator.consolidate(
        memory,
        max_age_hours=max_age_hours
    )
    
    print(f"\n📦 Consolidation results:")
    print(f"   New semantic clusters: {len(new_clusters)}")
    print(f"   Archived episodic scars: {len(archived_ids)}")
    
    # Remove archived scars from episodic memory
    if not dry_run:
        for scar_id in archived_ids:
            if scar_id in memory.episodic:
                del memory.episodic[scar_id]
        
        # Add new clusters
        for cluster in new_clusters:
            memory.add_semantic(cluster)
        
        # Save
        memory.save()
        
        # Verify chain integrity hasn't been affected
        if not chain.verify_chain():
            print("❌ ERROR: Chain integrity compromised after consolidation!")
            return 1
    
    print(f"\n📊 After consolidation:")
    print(f"   Episodic scars: {len(memory.episodic)}")
    print(f"   Semantic clusters: {len(memory.semantic)}")
    print(f"   Archetypes: {len(memory.archetypes)}")
    
    print(f"\n✅ Sleep cycle completed at {datetime.utcnow().isoformat()}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SCM Sleep Scheduler")
    parser.add_argument("--chain", default="chain.wal", help="Path to chain.wal")
    parser.add_argument("--memory", default="memory.db", help="Path to memory database")
    parser.add_argument("--max-age", type=float, default=72, help="Max age in hours before consolidation")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually modify memory")
    
    args = parser.parse_args()
    
    from datetime import datetime
    import hashlib
    
    exit(asyncio.run(run_sleep_cycle(
        chain_path=args.chain,
        memory_path=args.memory,
        max_age_hours=args.max_age,
        dry_run=args.dry_run
    )))
