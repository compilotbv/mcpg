"""
User and permission management for PostgreSQL (DCL).
"""

import logging
from typing import Any, Dict, List, Optional
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class UserManager:
    """Handles DCL operations for PostgreSQL users and permissions."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the user manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def list_users(self) -> Dict[str, Any]:
        """
        List all database users/roles.
        
        Returns:
            List of users
        """
        query = """
            SELECT 
                rolname as username,
                rolsuper as is_superuser,
                rolcreaterole as can_create_role,
                rolcreatedb as can_create_db,
                rolcanlogin as can_login,
                rolconnlimit as connection_limit,
                valuntil as password_expiry
            FROM pg_roles
            WHERE rolname NOT LIKE 'pg_%'
            ORDER BY rolname
        """
        try:
            results = self.db.execute_query(query, fetch=True)
            return {
                "success": True,
                "users": results
            }
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_user(
        self,
        username: str,
        password: Optional[str] = None,
        can_login: bool = True,
        can_create_db: bool = False,
        can_create_role: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new database user.
        
        Args:
            username: Username for the new user
            password: Password (optional)
            can_login: Whether user can login
            can_create_db: Whether user can create databases
            can_create_role: Whether user can create roles
        
        Returns:
            Operation result
        """
        try:
            options = []
            if can_login:
                options.append("LOGIN")
            else:
                options.append("NOLOGIN")
            
            if can_create_db:
                options.append("CREATEDB")
            
            if can_create_role:
                options.append("CREATEROLE")
            
            if password:
                options.append(f"PASSWORD '{password}'")
            
            options_sql = " ".join(options)
            query = f"CREATE ROLE {username} {options_sql}"
            
            self.db.execute_query(query, fetch=False)
            
            return {
                "success": True,
                "message": f"User {username} created successfully"
            }
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def grant_permissions(
        self,
        username: str,
        privileges: str,
        object_type: str,
        object_name: str,
        schema: str = "public"
    ) -> Dict[str, Any]:
        """
        Grant permissions to a user.
        
        Args:
            username: Username to grant permissions to
            privileges: Privileges to grant (e.g., "SELECT", "INSERT", "ALL")
            object_type: Type of object ("TABLE", "DATABASE", "SCHEMA", etc.)
            object_name: Name of the object
            schema: Schema name (for tables)
        
        Returns:
            Operation result
        """
        try:
            if object_type.upper() == "TABLE":
                full_name = f"{schema}.{object_name}"
            else:
                full_name = object_name
            
            query = f"GRANT {privileges} ON {object_type} {full_name} TO {username}"
            
            self.db.execute_query(query, fetch=False)
            
            return {
                "success": True,
                "message": f"Granted {privileges} on {object_type} {full_name} to {username}"
            }
        except Exception as e:
            logger.error(f"Failed to grant permissions: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def revoke_permissions(
        self,
        username: str,
        privileges: str,
        object_type: str,
        object_name: str,
        schema: str = "public"
    ) -> Dict[str, Any]:
        """
        Revoke permissions from a user.
        
        Args:
            username: Username to revoke permissions from
            privileges: Privileges to revoke
            object_type: Type of object
            object_name: Name of the object
            schema: Schema name (for tables)
        
        Returns:
            Operation result
        """
        try:
            if object_type.upper() == "TABLE":
                full_name = f"{schema}.{object_name}"
            else:
                full_name = object_name
            
            query = f"REVOKE {privileges} ON {object_type} {full_name} FROM {username}"
            
            self.db.execute_query(query, fetch=False)
            
            return {
                "success": True,
                "message": f"Revoked {privileges} on {object_type} {full_name} from {username}"
            }
        except Exception as e:
            logger.error(f"Failed to revoke permissions: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_permissions(self, username: str) -> Dict[str, Any]:
        """
        List permissions for a user.
        
        Args:
            username: Username to list permissions for
        
        Returns:
            User permissions
        """
        query = """
            SELECT 
                n.nspname as schema,
                c.relname as object_name,
                c.relkind as object_type,
                r.rolname as grantee,
                p.privilege_type
            FROM information_schema.role_table_grants p
            JOIN pg_class c ON p.table_name = c.relname
            JOIN pg_namespace n ON c.relnamespace = n.oid
            JOIN pg_roles r ON p.grantee = r.rolname
            WHERE r.rolname = %s
            ORDER BY n.nspname, c.relname
        """
        try:
            results = self.db.execute_query(query, (username,), fetch=True)
            return {
                "success": True,
                "permissions": results,
                "user": username
            }
        except Exception as e:
            logger.error(f"Failed to list permissions: {e}")
            return {
                "success": False,
                "error": str(e)
            }

