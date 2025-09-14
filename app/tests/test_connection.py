# test_connection.py
import asyncio
import asyncpg
import os

async def test_connection():
    try:
        # Use the same connection string your tests should use
        conn = await asyncpg.connect(
            user='test_user',
            password='test_password',
            database='test_db',
            host='localhost',  # or 'postgres' if inside docker network
            port=5432
        )
        print("✅ Successfully connected to PostgreSQL!")
        
        # Try to create a simple table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name TEXT
            )
        ''')
        print("✅ Successfully created test table!")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())