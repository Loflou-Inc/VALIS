"""
VALIS 2.0 Database Client
PostgreSQL connection and helper functions
"""
import psycopg2
import psycopg2.pool
import os
import json
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

class DatabaseClient:
    def __init__(self):
        self.connection_pool = None
        self._init_connection_pool()
    
    def _init_connection_pool(self):
        """Initialize PostgreSQL connection pool"""
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'valis2'),
            'user': os.getenv('DB_USER', 'valis'),
            'password': os.getenv('DB_PASSWORD', 'valis123')
        }
        
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,  # min/max connections
                **db_config
            )
            print(f"Database pool initialized: {db_config['host']}:{db_config['port']}")
        except Exception as e:
            print(f"Failed to initialize database pool: {e}")
            self.connection_pool = None
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool"""
        if not self.connection_pool:
            raise Exception("Database pool not initialized")
        
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    def query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results as list of dicts"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return [dict(zip(columns, row)) for row in rows]
    
    def execute(self, sql: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE and return affected rows"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                conn.commit()
                return cur.rowcount
    
    def insert(self, table: str, values: Dict[str, Any]) -> str:
        """Insert row and return UUID"""
        columns = list(values.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders}) RETURNING id"
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(values.values()))
                conn.commit()
                return cur.fetchone()[0]

# Global instance
db = DatabaseClient()
