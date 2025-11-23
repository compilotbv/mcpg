"""
Query execution utilities for PostgreSQL operations.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class QueryExecutor:
    """Handles execution of various PostgreSQL queries."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the query executor.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def execute_select_query(self, query: str, params: Optional[Tuple] = None) -> Dict[str, Any]:
        """
        Execute a SELECT query.
        
        Args:
            query: SQL SELECT query
            params: Query parameters
        
        Returns:
            Query results with metadata
        """
        try:
            results = self.db.execute_query(query, params, fetch=True)
            return {
                "success": True,
                "rows": results,
                "row_count": len(results) if results else 0
            }
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_explain(self, query: str, params: Optional[Tuple] = None) -> Dict[str, Any]:
        """
        Execute EXPLAIN on a query.
        
        Args:
            query: SQL query to explain
            params: Query parameters
        
        Returns:
            Query execution plan
        """
        try:
            explain_query = f"EXPLAIN (FORMAT JSON, ANALYZE FALSE) {query}"
            results = self.db.execute_query(explain_query, params, fetch=True)
            return {
                "success": True,
                "plan": results[0] if results else None
            }
        except Exception as e:
            logger.error(f"EXPLAIN failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_databases(self) -> Dict[str, Any]:
        """
        List all databases.
        
        Returns:
            List of databases
        """
        query = """
            SELECT datname as name, 
                   pg_size_pretty(pg_database_size(datname)) as size,
                   pg_encoding_to_char(encoding) as encoding
            FROM pg_database
            WHERE datistemplate = false
            ORDER BY datname
        """
        try:
            results = self.db.execute_query(query, fetch=True)
            return {
                "success": True,
                "databases": results
            }
        except Exception as e:
            logger.error(f"Failed to list databases: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_tables(self, schema: str = "public") -> Dict[str, Any]:
        """
        List all tables in a schema.
        
        Args:
            schema: Schema name (default: public)
        
        Returns:
            List of tables
        """
        query = """
            SELECT 
                table_schema,
                table_name,
                table_type
            FROM information_schema.tables
            WHERE table_schema = %s
            ORDER BY table_name
        """
        try:
            results = self.db.execute_query(query, (schema,), fetch=True)
            return {
                "success": True,
                "tables": results,
                "schema": schema
            }
        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_columns(self, table_name: str, schema: str = "public") -> Dict[str, Any]:
        """
        Get column information for a table.
        
        Args:
            table_name: Name of the table
            schema: Schema name (default: public)
        
        Returns:
            Column information
        """
        query = """
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        try:
            results = self.db.execute_query(query, (schema, table_name), fetch=True)
            return {
                "success": True,
                "columns": results,
                "table": table_name,
                "schema": schema
            }
        except Exception as e:
            logger.error(f"Failed to list columns: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_table_info(self, table_name: str, schema: str = "public") -> Dict[str, Any]:
        """
        Get detailed table information including indexes and constraints.
        
        Args:
            table_name: Name of the table
            schema: Schema name (default: public)
        
        Returns:
            Detailed table information
        """
        try:
            # Get columns
            columns_result = self.list_columns(table_name, schema)
            
            # Get indexes
            indexes_query = """
                SELECT 
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = %s AND tablename = %s
            """
            indexes = self.db.execute_query(indexes_query, (schema, table_name), fetch=True)
            
            # Get constraints
            constraints_query = """
                SELECT 
                    con.conname as constraint_name,
                    con.contype as constraint_type,
                    pg_get_constraintdef(con.oid) as definition
                FROM pg_constraint con
                JOIN pg_class rel ON rel.oid = con.conrelid
                JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
                WHERE nsp.nspname = %s AND rel.relname = %s
            """
            constraints = self.db.execute_query(constraints_query, (schema, table_name), fetch=True)
            
            # Get table size
            size_query = """
                SELECT pg_size_pretty(pg_total_relation_size(%s)) as total_size
            """
            size_result = self.db.execute_query(
                size_query,
                (f"{schema}.{table_name}",),
                fetch=True
            )
            
            return {
                "success": True,
                "table": table_name,
                "schema": schema,
                "columns": columns_result.get("columns", []),
                "indexes": indexes,
                "constraints": constraints,
                "size": size_result[0]["total_size"] if size_result else "Unknown"
            }
        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_database_size(self) -> Dict[str, Any]:
        """
        Get database and table sizes.
        
        Returns:
            Size information
        """
        query = """
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY size_bytes DESC
            LIMIT 50
        """
        try:
            tables = self.db.execute_query(query, fetch=True)
            
            db_size_query = "SELECT pg_size_pretty(pg_database_size(current_database())) as database_size"
            db_size = self.db.execute_query(db_size_query, fetch=True)
            
            return {
                "success": True,
                "database_size": db_size[0]["database_size"] if db_size else "Unknown",
                "tables": tables
            }
        except Exception as e:
            logger.error(f"Failed to get database size: {e}")
            return {
                "success": False,
                "error": str(e)
            }

