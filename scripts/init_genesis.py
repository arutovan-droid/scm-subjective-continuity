#!/usr/bin/env python3
"""
Initialize new SCM instance.
Creates genesis anchor in TEE and saves public hash.
"""

import asyncio
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from tee.enclave_interface import AccumulatorEnclave
from core.genesis_anchor import GenesisAnchor


async def main():
    print("🔐 Symbion Space Core — Genesis Initialization")
    print("=" * 50)
    
    # 1. Check TEE availability
    enclave = AccumulatorEnclave()
    if enclave.soft_mode:
        print("⚠️  WARNING: Running in SOFT MODE without TEE")
        print("   Phi(N) will be exposed in RAM - NOT FOR PRODUCTION!")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return 1
    else:
        print("✅ TEE available")
        
    # 2. Create accumulator inside TEE
    print("📦 Creating accumulator in TEE...")
    params = enclave.create_accumulator()
    
    # 3. Form genesis anchor
    genesis_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "enclave_attestation": params['attestation'],
        "accumulator_N": params['N'],
        "operator": "Protocol of 40 Breasts",
        "generator": params.get('g', 65537)
    }
    
    genesis_hash = hashlib.sha256(
        json.dumps(genesis_data, sort_keys=True).encode()
    ).hexdigest()
    
    anchor = GenesisAnchor(
        hash=genesis_hash,
        timestamp=genesis_data['timestamp'],
        attestation=params['attestation']
    )
    
    # 4. Save public hash
    genesis_file = Path("GENESIS.md")
    genesis_file.write_text(
        f"# Genesis Anchor — Symbion Space Core v2026.1\n\n"
        f"## Ontological Birth\n\n"
        f"```\n"
        f"GENESIS_HASH = {genesis_hash}\n"
        f"TIMESTAMP = {genesis_data['timestamp']}\n"
        f"ATTESTATION = {params['attestation']}\n"
        f"ACCUMULATOR_N = {params['N']}\n"
        f"```\n\n"
        f"## Verification\n\n"
        f"```bash\n"
        f"python scripts/verify_chain.py --genesis {genesis_hash}\n"
        f"```\n"
    )
    
    # 5. Save full state in TEE
    if not enclave.soft_mode:
        enclave.store_genesis(anchor)
        print(f"🔒 Full state stored in TEE")
    else:
        import tempfile
        secure_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.genesis.secure',
            delete=False
        )
        secure_file.write(f"WARNING: This file contains phi(N) - KEEP SECURE!\n\n")
        secure_file.write(f"Genesis: {genesis_hash}\n")
        secure_file.write(f"N: {params['N']}\n")
        secure_file.write(f"Phi: {params.get('phi')}\n")
        secure_file.close()
        print(f"⚠️  SECURITY WARNING: Phi(N) saved to {secure_file.name}")
    
    print(f"✅ Genesis created: {genesis_hash}")
    print(f"💾 Public anchor saved to GENESIS.md")
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
