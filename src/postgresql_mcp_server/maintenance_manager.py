"""
Database maintenance and utility operations for PostgreSQL.
"""

import logging
import subprocess
import os
from typing import Any, Dict, Optional
from datetime import datetime
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class MaintenanceManager:
    """Handles database maintenance, backup, and utility operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the maintenance manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def vacuum_analyze(
        self,
        table_name: Optional[str] = None,
        schema: str = "public",
        full: bool = False
    ) -> Dict[str, Any]:
        """
        Run VACUUM and ANALYZE on a table or entire database.
        
        Args:
            table_name: Name of the table (None for entire database)
            schema: Schema name (default: public)
            full: Whether to run VACUUM FULL
        
        Returns:
            Operation result
        """
        try:
            vacuum_type = "VACUUM FULL" if full else "VACUUM"
            
            if table_name:
                query = f"{vacuum_type} ANALYZE {schema}.{table_name}"
            else:
                query = f"{vacuum_type} ANALYZE"
            
            # VACUUM cannot run inside a transaction block, so we need special handling
            with self.db.get_connection() as conn:
                conn.set_isolation_level(0)  # AUTOCOMMIT mode
                cursor = conn.cursor()
                cursor.execute(query)
                cursor.close()
            
            return {
                "success": True,
                "message": f"VACUUM ANALYZE completed for {table_name or 'entire database'}"
            }
        except Exception as e:
            logger.error(f"Failed to run VACUUM ANALYZE: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def backup_database(
        self,
        output_file: Optional[str] = None,
        format: str = "custom"
    ) -> Dict[str, Any]:
        """
        Create a database backup using pg_dump.
        
        Args:
            output_file: Output file path (None for auto-generated name)
            format: Dump format (custom, plain, directory, tar)
        
        Returns:
            Operation result with backup file path
        """
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"/tmp/backup_{self.db.database}_{timestamp}.dump"
            
            format_flags = {
                "custom": "-Fc",
                "plain": "-Fp",
                "directory": "-Fd",
                "tar": "-Ft"
            }
            
            format_flag = format_flags.get(format, "-Fc")
            
            # Build pg_dump command
            cmd = [
                "pg_dump",
                "-h", self.db.host,
                "-p", str(self.db.port),
                "-U", self.db.user,
                "-d", self.db.database,
                format_flag,
                "-f", output_file
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db.password
            
            # Execute pg_dump
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Database backup created successfully",
                    "backup_file": output_file
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def restore_database(
        self,
        backup_file: str,
        clean: bool = False
    ) -> Dict[str, Any]:
        """
        Restore a database from backup using pg_restore.
        
        Args:
            backup_file: Path to backup file
            clean: Whether to clean (drop) database objects before restoring
        
        Returns:
            Operation result
        """
        try:
            # Build pg_restore command
            cmd = [
                "pg_restore",
                "-h", self.db.host,
                "-p", str(self.db.port),
                "-U", self.db.user,
                "-d", self.db.database,
            ]
            
            if clean:
                cmd.append("--clean")
            
            cmd.append(backup_file)
            
            # Set password environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db.password
            
            # Execute pg_restore
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Database restored successfully"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def kill_connections(self, target_database: Optional[str] = None) -> Dict[str, Any]:
        """
        Terminate active connections to a database.
        
        Args:
            target_database: Database name (None for current database)
        
        Returns:
            Operation result
        """
        try:
            database = target_database or self.db.database
            
            query = """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s
                AND pid <> pg_backend_pid()
            """
            
            results = self.db.execute_query(query, (database,), fetch=True)
            terminated_count = sum(1 for r in results if list(r.values())[0])
            
            return {
                "success": True,
                "message": f"Terminated {terminated_count} connections to {database}",
                "terminated_count": terminated_count
            }
        except Exception as e:
            logger.error(f"Failed to kill connections: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_active_connections(self) -> Dict[str, Any]:
        """
        Get information about active connections.
        
        Returns:
            Active connection information
        """
        query = """
            SELECT 
                datname as database,
                usename as username,
                application_name,
                client_addr,
                state,
                query,
                query_start
            FROM pg_stat_activity
            WHERE pid <> pg_backend_pid()
            ORDER BY query_start DESC
        """
        try:
            results = self.db.execute_query(query, fetch=True)
            return {
                "success": True,
                "connections": results,
                "connection_count": len(results) if results else 0
            }
        except Exception as e:
            logger.error(f"Failed to get active connections: {e}")
            return {
                "success": False,
                "error": str(e)
            }

