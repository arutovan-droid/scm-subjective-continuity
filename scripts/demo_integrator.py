#!/usr/bin/env python3
"""
Demo of Cognitive Integrator with SCM scars.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.cognitive_integrator import demonstrate_integration


async def main():
    print("=" * 60)
    print("🧠 COGNITIVE INTEGRATOR DEMO")
    print("=" * 60)
    
    integrator = await demonstrate_integration()
    
    print("\n" + "=" * 60)
    print("✅ Demo complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
