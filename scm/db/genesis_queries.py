# scm/db/genesis_queries.py
"""
PostgreSQL queries for quantum-safe genesis anchor storage.
"""

from typing import Optional, Dict, Any
import uuid
from datetime import datetime

class GenesisStorage:
    """Handles storage and retrieval of hybrid genesis anchors"""
    
    @staticmethod
    async def create_table(conn):
        """Create genesis_anchor table if not exists"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS genesis_anchor (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                anchor_hash TEXT UNIQUE NOT NULL,
                ed25519_public BYTEA NOT NULL,
                dilithium5_public BYTEA NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                physical_anchor_id TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                metadata JSONB DEFAULT '{}'::jsonb
            )
        """)
    
    @staticmethod
    async def store_anchor(conn, anchor_hash: str,
                          ed25519_public: bytes,
                          dilithium5_public: bytes,
                          physical_anchor_id: Optional[str] = None,
                          metadata: Optional[Dict] = None) -> str:
        """Store a new quantum genesis anchor"""
        record_id = str(uuid.uuid4())
        
        await conn.execute("""
            INSERT INTO genesis_anchor 
            (id, anchor_hash, ed25519_public, dilithium5_public, physical_anchor_id, metadata)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, record_id, anchor_hash, ed25519_public, dilithium5_public,
            physical_anchor_id, metadata or {})
        
        return record_id
    
    @staticmethod
    async def get_anchor_by_hash(conn, anchor_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve genesis anchor by its hash"""
        row = await conn.fetchrow("""
            SELECT id, anchor_hash, ed25519_public, dilithium5_public,
                   created_at, physical_anchor_id, metadata
            FROM genesis_anchor
            WHERE anchor_hash = $1 AND is_active = TRUE
        """, anchor_hash)
        
        if not row:
            return None
            
        return {
            'id': row['id'],
            'anchor_hash': row['anchor_hash'],
            'ed25519_public': bytes(row['ed25519_public']),
            'dilithium5_public': bytes(row['dilithium5_public']),
            'created_at': row['created_at'],
            'physical_anchor_id': row['physical_anchor_id'],
            'metadata': row['metadata']
        }
