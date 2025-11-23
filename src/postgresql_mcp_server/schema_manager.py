"""
Schema management operations for PostgreSQL (DDL).
"""

import logging
from typing import Any, Dict, List, Optional
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class SchemaManager:
    """Handles DDL operations for PostgreSQL schemas."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the schema manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def create_table(
        self,
        table_name: str,
        columns: List[Dict[str, str]],
        schema: str = "public"
    ) -> Dict[str, Any]:
        """
        Create a new table.
        
        Args:
            table_name: Name of the table to create
            columns: List of column definitions (name, type, constraints)
            schema: Schema name (default: public)
        
        Returns:
            Operation result
        """
        try:
            # Build column definitions
            column_defs = []
            for col in columns:
                col_def = f"{col['name']} {col['type']}"
                if col.get('constraints'):
                    col_def += f" {col['constraints']}"
                column_defs.append(col_def)
            
            columns_sql = ", ".join(column_defs)
            query = f"CREATE TABLE {schema}.{table_name} ({columns_sql})"
            
            self.db.execute_query(query, fetch=False)
            
            return {
                "success": True,
                "message": f"Table {schema}.{table_name} created successfully"
            }
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def drop_table(
        self,
        table_name: str,
        schema: str = "public",
        cascade: bool = False
    ) -> Dict[str, Any]:
        """
        Drop a table.
        
        Args:
            table_name: Name of the table to drop
            schema: Schema name (default: public)
            cascade: Whether to cascade drop
        
        Returns:
            Operation result
        """
        try:
            cascade_sql = "CASCADE" if cascade else ""
            query = f"DROP TABLE {schema}.{table_name} {cascade_sql}"
            
            self.db.execute_query(query, fetch=False)
            
            return {
                "success": True,
                "message": f"Table {schema}.{table_name} dropped successfully"
            }
        except Exception as e:
            logger.error(f"Failed to drop table: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def alter_table(
        self,
        table_name: str,
        action: str,
        schema: str = "public"
    ) -> Dict[str, Any]:
        """
        Alter a table structure.
        
        Args:
            table_name: Name of the table
            action: ALTER TABLE action (e.g., "ADD COLUMN name VARCHAR(100)")
            schema: Schema name (default: public)
        
        Returns:
            Operation result
        """
        try:
            query = f"ALTER TABLE {schema}.{table_name} {action}"
            
            self.db.execute_query(query, fetch=False)
            
            return {
                "success": True,
                "message": f"Table {schema}.{table_name} altered successfully"
            }
        except Exception as e:
            logger.error(f"Failed to alter table: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_index(
        self,
        index_name: str,
        table_name: str,
        columns: List[str],
        schema: str = "public",
        unique: bool = False
    ) -> Dict[str, Any]:
        """
        Create an index.
        
        Args:
            index_name: Name of the index
            table_name: Name of the table
            columns: List of column names
            schema: Schema name (default: public)
            unique: Whether to create a unique index
        
        Returns:
            Operation result
        """
        try:
            unique_sql = "UNIQUE" if unique else ""
            columns_sql = ", ".join(columns)
            query = f"CREATE {unique_sql} INDEX {index_name} ON {schema}.{table_name} ({columns_sql})"
            
            self.db.execute_query(query, fetch=False)
            
            return {
                "success": True,
                "message": f"Index {index_name} created successfully"
            }
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def drop_index(
        self,
        index_name: str,
        schema: str = "public",
        cascade: bool = False
    ) -> Dict[str, Any]:
        """
        Drop an index.
        
        Args:
            index_name: Name of the index
            schema: Schema name (default: public)
            cascade: Whether to cascade drop
        
        Returns:
            Operation result
        """
        try:
            cascade_sql = "CASCADE" if cascade else ""
            query = f"DROP INDEX {schema}.{index_name} {cascade_sql}"
            
            self.db.execute_query(query, fetch=False)
            
            return {
                "success": True,
                "message": f"Index {index_name} dropped successfully"
            }
        except Exception as e:
            logger.error(f"Failed to drop index: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_table_ddl(self, table_name: str, schema: str = "public") -> Dict[str, Any]:
        """
        Generate CREATE TABLE statement for an existing table.
        
        Args:
            table_name: Name of the table
            schema: Schema name (default: public)
        
        Returns:
            DDL statement
        """
        try:
            # Get column definitions
            columns_query = """
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
            columns = self.db.execute_query(columns_query, (schema, table_name), fetch=True)
            
            # Build CREATE TABLE statement
            column_defs = []
            for col in columns:
                col_def = f"{col['column_name']} {col['data_type']}"
                if col['character_maximum_length']:
                    col_def += f"({col['character_maximum_length']})"
                if col['is_nullable'] == 'NO':
                    col_def += " NOT NULL"
                if col['column_default']:
                    col_def += f" DEFAULT {col['column_default']}"
                column_defs.append(col_def)
            
            ddl = f"CREATE TABLE {schema}.{table_name} (\n  "
            ddl += ",\n  ".join(column_defs)
            ddl += "\n);"
            
            return {
                "success": True,
                "ddl": ddl
            }
        except Exception as e:
            logger.error(f"Failed to get table DDL: {e}")
            return {
                "success": False,
                "error": str(e)
            }

