"""
Test connections to PostgreSQL and Redis
Run with: python test_db_connection.py
"""

import asyncio
import asyncpg
import redis.asyncio as redis
import uuid
import json
from datetime import datetime

async def test_postgres():
    print("\n📦 Testing PostgreSQL...")
    try:
        conn = await asyncpg.connect(
            user='scm',
            password='scm_dev_password',
            database='scm_chain',
            host='localhost',
            port=5432
        )
        
        # Insert test scar
        scar_id = uuid.uuid4()
        await conn.execute('''
            INSERT INTO scars (
                id, genesis_ref, incident_type, cognitive_basis,
                collision_mode, pre_state_hash, post_state_hash,
                deformation_vector, entropy_score, ontological_drift,
                timestamp, operator_id
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        ''',
            scar_id,
            'test_genesis',
            'test',
            'ru',
            False,
            'pre_hash',
            'post_hash',
            '{}',
            0.5,
            0.1,
            datetime.utcnow(),
            'test_operator'
        )
        
        # Read back
        row = await conn.fetchrow("SELECT * FROM scars WHERE id = $1", scar_id)
        print(f"✅ PostgreSQL: Scar {row['id']} created")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL error: {e}")
        return False

async def test_redis():
    print("\n📦 Testing Redis...")
    try:
        client = redis.from_url("redis://localhost:6379/0")
        
        # Set test data
        test_key = f"test:{uuid.uuid4()}"
        await client.set(test_key, "SCM test data")
        await client.expire(test_key, 10)
        
        # Read back
        value = await client.get(test_key)
        print(f"✅ Redis: {value.decode()}")
        
        await client.aclose()
        return True
    except Exception as e:
        print(f"❌ Redis error: {e}")
        return False

async def main():
    print("🔌 Testing database connections...")
    pg_ok = await test_postgres()
    redis_ok = await test_redis()
    
    print("\n" + "="*40)
    if pg_ok and redis_ok:
        print("✅ ALL SYSTEMS GO! PostgreSQL and Redis are working.")
    else:
        print("⚠️ Some services are not available.")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(main())
