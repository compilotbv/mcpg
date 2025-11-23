"""
Data manipulation operations for PostgreSQL (DML).
"""

import logging
import json
from typing import Any, Dict, List, Optional, Tuple
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class DataManager:
    """Handles DML operations for PostgreSQL data."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the data manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def insert_data(
        self,
        table_name: str,
        data: Dict[str, Any],
        schema: str = "public"
    ) -> Dict[str, Any]:
        """
        Insert a row into a table.
        
        Args:
            table_name: Name of the table
            data: Dictionary of column:value pairs
            schema: Schema name (default: public)
        
        Returns:
            Operation result
        """
        try:
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ", ".join(["%s"] * len(values))
            columns_sql = ", ".join(columns)
            
            query = f"INSERT INTO {schema}.{table_name} ({columns_sql}) VALUES ({placeholders}) RETURNING *"
            
            result = self.db.execute_query(query, tuple(values), fetch=True)
            
            return {
                "success": True,
                "message": f"Row inserted into {schema}.{table_name}",
                "inserted_row": result[0] if result else None
            }
        except Exception as e:
            logger.error(f"Failed to insert data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def bulk_insert(
        self,
        table_name: str,
        data_list: List[Dict[str, Any]],
        schema: str = "public"
    ) -> Dict[str, Any]:
        """
        Insert multiple rows into a table.
        
        Args:
            table_name: Name of the table
            data_list: List of dictionaries with column:value pairs
            schema: Schema name (default: public)
        
        Returns:
            Operation result
        """
        try:
            if not data_list:
                return {
                    "success": False,
                    "error": "No data provided"
                }
            
            # Use first row to determine columns
            columns = list(data_list[0].keys())
            columns_sql = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            
            query = f"INSERT INTO {schema}.{table_name} ({columns_sql}) VALUES ({placeholders})"
            
            # Prepare values list
            values_list = [tuple(row[col] for col in columns) for row in data_list]
            
            self.db.execute_many(query, values_list)
            
            return {
                "success": True,
                "message": f"Inserted {len(data_list)} rows into {schema}.{table_name}",
                "row_count": len(data_list)
            }
        except Exception as e:
            logger.error(f"Failed to bulk insert data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_data(
        self,
        table_name: str,
        data: Dict[str, Any],
        where_clause: str,
        where_params: Optional[Tuple] = None,
        schema: str = "public"
    ) -> Dict[str, Any]:
        """
        Update rows in a table.
        
        Args:
            table_name: Name of the table
            data: Dictionary of column:value pairs to update
            where_clause: WHERE clause (without WHERE keyword)
            where_params: Parameters for WHERE clause
            schema: Schema name (default: public)
        
        Returns:
            Operation result
        """
        try:
            set_clauses = [f"{col} = %s" for col in data.keys()]
            set_sql = ", ".join(set_clauses)
            
            query = f"UPDATE {schema}.{table_name} SET {set_sql} WHERE {where_clause} RETURNING *"
            
            params = tuple(list(data.values()) + list(where_params or []))
            result = self.db.execute_query(query, params, fetch=True)
            
            return {
                "success": True,
                "message": f"Updated {len(result) if result else 0} rows in {schema}.{table_name}",
                "updated_rows": result,
                "row_count": len(result) if result else 0
            }
        except Exception as e:
            logger.error(f"Failed to update data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_data(
        self,
        table_name: str,
        where_clause: str,
        where_params: Optional[Tuple] = None,
        schema: str = "public"
    ) -> Dict[str, Any]:
        """
        Delete rows from a table.
        
        Args:
            table_name: Name of the table
            where_clause: WHERE clause (without WHERE keyword)
            where_params: Parameters for WHERE clause
            schema: Schema name (default: public)
        
        Returns:
            Operation result
        """
        try:
            query = f"DELETE FROM {schema}.{table_name} WHERE {where_clause} RETURNING *"
            
            result = self.db.execute_query(query, where_params, fetch=True)
            
            return {
                "success": True,
                "message": f"Deleted {len(result) if result else 0} rows from {schema}.{table_name}",
                "deleted_rows": result,
                "row_count": len(result) if result else 0
            }
        except Exception as e:
            logger.error(f"Failed to delete data: {e}")
            return {
                "success": False,
                "error": str(e)
            }

