"""
VALIS 2.0 Database Client - REFACTORED FOR SPRINT 1.3
PostgreSQL connection and helper functions with secure configuration management
"""
import psycopg2
import psycopg2.pool
import os
import json
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

from core.config import get_config
from core.exceptions import DatabaseError, ConfigurationError
from core.logging_config import get_valis_logger

class DatabaseClient:
    def __init__(self, config=None):
        self.logger = get_valis_logger()
        self.connection_pool = None
        
        # Use provided config or load from environment
        try:
            self.config = config or get_config()
        except ConfigurationError as e:
            self.logger.critical(f"Database configuration failed: {e}")
            raise DatabaseError(f"Cannot initialize database: {e}")
        
        self._init_connection_pool()
    
    def _init_connection_pool(self):
        """Initialize PostgreSQL connection pool with secure configuration"""
        db_config = {
            'host': self.config.db_host,
            'port': self.config.db_port,
            'database': self.config.db_name,
            'user': self.config.db_user,
            'password': self.config.db_password  # NO DEFAULT - Must be in environment
        }
        
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,  # min/max connections
                **db_config
            )
            self.logger.info(
                f"Database pool initialized: {db_config['host']}:{db_config['port']}/{db_config['database']}"
            )
        except psycopg2.Error as e:
            self.logger.critical(f"PostgreSQL connection failed: {e}")
            raise DatabaseError(f"Failed to connect to database: {e}")
        except Exception as e:
            self.logger.critical(f"Unexpected database initialization error: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool"""
        if not self.connection_pool:
            raise DatabaseError("Database pool not initialized")
        
        conn = None
        try:
            conn = self.connection_pool.getconn()
            if conn is None:
                raise DatabaseError("Unable to get connection from pool")
            yield conn
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database connection error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    def query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results as list of dicts"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    columns = [desc[0] for desc in cur.description]
                    rows = cur.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
        except psycopg2.Error as e:
            self.logger.error(f"Query execution failed: {e}", extra={'sql': sql[:100]})
            raise DatabaseError(f"Query failed: {e}")
    
    def execute(self, sql: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE and return affected rows"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    conn.commit()
                    return cur.rowcount
        except psycopg2.Error as e:
            self.logger.error(f"Execute operation failed: {e}", extra={'sql': sql[:100]})
            raise DatabaseError(f"Execute failed: {e}")
    
    def insert(self, table: str, values: Dict[str, Any]) -> str:
        """Insert row and return UUID"""
        if not table or not values:
            raise DatabaseError("Table name and values are required for insert")
        
        try:
            columns = list(values.keys())
            placeholders = ', '.join(['%s'] * len(columns))
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders}) RETURNING id"
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, tuple(values.values()))
                    conn.commit()
                    result = cur.fetchone()
                    if result:
                        return result[0]
                    else:
                        raise DatabaseError("Insert did not return an ID")
        except psycopg2.Error as e:
            self.logger.error(f"Insert operation failed: {e}", extra={'table': table})
            raise DatabaseError(f"Insert failed: {e}")

# Global instance - initialized lazily to avoid test issues
_db_instance = None

def get_db():
    """Get database instance (lazy initialization)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseClient()
    return _db_instance

# For backward compatibility with existing code that uses `from memory.db import db`
class DatabaseProxy:
    def __getattr__(self, name):
        return getattr(get_db(), name)

db = DatabaseProxy()