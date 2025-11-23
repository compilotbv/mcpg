"""
Database connection manager for PostgreSQL.
Handles connection pooling, validation, and lifecycle management.
"""

import os
import logging
from typing import Optional, Any, Dict, List, Tuple
from contextlib import contextmanager
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages PostgreSQL database connections with connection pooling."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        min_conn: int = 1,
        max_conn: int = 10,
        readonly: bool = False,
        sslmode: str = "prefer"
    ):
        """
        Initialize the database manager.
        
        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            database: Database name
            user: Database user
            password: Database password
            min_conn: Minimum connections in pool
            max_conn: Maximum connections in pool
            readonly: Whether to operate in read-only mode
            sslmode: SSL mode for connection
        """
        self.host = host or os.getenv("POSTGRES_HOST", "localhost")
        self.port = port or int(os.getenv("POSTGRES_PORT", "5432"))
        self.database = database or os.getenv("POSTGRES_DB", "postgres")
        self.user = user or os.getenv("POSTGRES_USER", "postgres")
        self.password = password or os.getenv("POSTGRES_PASSWORD", "")
        self.min_conn = min_conn
        self.max_conn = max_conn
        self.readonly = readonly or os.getenv("POSTGRES_READONLY", "false").lower() == "true"
        self.sslmode = sslmode or os.getenv("POSTGRES_SSLMODE", "prefer")
        
        self._pool: Optional[pool.ThreadedConnectionPool] = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the connection pool."""
        if self._initialized:
            return
        
        try:
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                self.min_conn,
                self.max_conn,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                sslmode=self.sslmode,
                connect_timeout=10
            )
            self._initialized = True
            logger.info(f"Database connection pool initialized for {self.host}:{self.port}/{self.database}")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Yields:
            A database connection
        """
        if not self._initialized:
            self.initialize()
        
        conn = None
        try:
            conn = self._pool.getconn()
            if self.readonly:
                conn.set_session(readonly=True)
            yield conn
        finally:
            if conn:
                self._pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, dict_cursor: bool = True):
        """
        Get a cursor from a pooled connection.
        
        Args:
            dict_cursor: Whether to use RealDictCursor (returns dict rows)
        
        Yields:
            A database cursor
        """
        with self.get_connection() as conn:
            cursor_factory = RealDictCursor if dict_cursor else None
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Database error: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None,
        fetch: bool = True
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            fetch: Whether to fetch results
        
        Returns:
            Query results if fetch=True, None otherwise
        """
        with self.get_cursor(dict_cursor=True) as cursor:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            return None
    
    def execute_many(
        self,
        query: str,
        params_list: List[Tuple]
    ) -> None:
        """
        Execute a SQL query multiple times with different parameters.
        
        Args:
            query: SQL query to execute
            params_list: List of parameter tuples
        """
        with self.get_cursor(dict_cursor=False) as cursor:
            cursor.executemany(query, params_list)
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the database connection.
        
        Returns:
            Connection status information
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT version(), current_database(), current_user")
                result = cursor.fetchone()
                return {
                    "status": "connected",
                    "version": result["version"],
                    "database": result["current_database"],
                    "user": result["current_user"],
                    "host": self.host,
                    "port": self.port
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def close(self) -> None:
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()
            self._initialized = False
            logger.info("Database connection pool closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


