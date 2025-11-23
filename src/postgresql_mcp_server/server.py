"""
PostgreSQL MCP Server - Main server implementation.
"""

import asyncio
import logging
import json
import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .db_manager import DatabaseManager
from .query_executor import QueryExecutor
from .schema_manager import SchemaManager
from .data_manager import DataManager
from .user_manager import UserManager
from .maintenance_manager import MaintenanceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class PostgreSQLMCPServer:
    """PostgreSQL MCP Server implementation."""
    
    def __init__(self):
        """Initialize the PostgreSQL MCP server."""
        self.server = Server("postgresql-mcp-server")
        self.db: Optional[DatabaseManager] = None
        self.query_executor: Optional[QueryExecutor] = None
        self.schema_manager: Optional[SchemaManager] = None
        self.data_manager: Optional[DataManager] = None
        self.user_manager: Optional[UserManager] = None
        self.maintenance_manager: Optional[MaintenanceManager] = None
        
        # Register handlers
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool
    
    def initialize_managers(self):
        """Initialize database managers."""
        self.db = DatabaseManager()
        self.db.initialize()
        
        self.query_executor = QueryExecutor(self.db)
        self.schema_manager = SchemaManager(self.db)
        self.data_manager = DataManager(self.db)
        self.user_manager = UserManager(self.db)
        self.maintenance_manager = MaintenanceManager(self.db)
        
        logger.info("Database managers initialized")
    
    async def list_tools(self) -> list[Tool]:
        """List available MCP tools."""
        return [
            # Query Execution Tools
            Tool(
                name="execute_query",
                description="Execute a SELECT query and return results",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL SELECT query to execute"},
                        "params": {"type": "array", "description": "Query parameters (optional)"}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="execute_explain",
                description="Get the execution plan for a query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL query to explain"}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="list_databases",
                description="List all databases in the PostgreSQL server",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="list_tables",
                description="List all tables in a schema",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "schema": {"type": "string", "description": "Schema name", "default": "public"}
                    }
                }
            ),
            Tool(
                name="list_columns",
                description="Get column information for a table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Table name"},
                        "schema": {"type": "string", "description": "Schema name", "default": "public"}
                    },
                    "required": ["table_name"]
                }
            ),
            Tool(
                name="get_table_info",
                description="Get detailed information about a table including columns, indexes, and constraints",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Table name"},
                        "schema": {"type": "string", "description": "Schema name", "default": "public"}
                    },
                    "required": ["table_name"]
                }
            ),
            Tool(
                name="get_database_size",
                description="Get size information for the database and its tables",
                inputSchema={"type": "object", "properties": {}}
            ),
            
            # Schema Management Tools (DDL)
            Tool(
                name="create_table",
                description="Create a new table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                        "columns": {
                            "type": "array",
                            "description": "Column definitions",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "constraints": {"type": "string"}
                                }
                            }
                        },
                        "schema": {"type": "string", "default": "public"}
                    },
                    "required": ["table_name", "columns"]
                }
            ),
            Tool(
                name="drop_table",
                description="Drop a table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Table name"},
                        "schema": {"type": "string", "default": "public"},
                        "cascade": {"type": "boolean", "default": False}
                    },
                    "required": ["table_name"]
                }
            ),
            Tool(
                name="alter_table",
                description="Alter a table structure",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Table name"},
                        "action": {"type": "string", "description": "ALTER TABLE action"},
                        "schema": {"type": "string", "default": "public"}
                    },
                    "required": ["table_name", "action"]
                }
            ),
            Tool(
                name="create_index",
                description="Create an index on a table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "index_name": {"type": "string", "description": "Index name"},
                        "table_name": {"type": "string", "description": "Table name"},
                        "columns": {"type": "array", "items": {"type": "string"}},
                        "schema": {"type": "string", "default": "public"},
                        "unique": {"type": "boolean", "default": False}
                    },
                    "required": ["index_name", "table_name", "columns"]
                }
            ),
            Tool(
                name="drop_index",
                description="Drop an index",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "index_name": {"type": "string", "description": "Index name"},
                        "schema": {"type": "string", "default": "public"},
                        "cascade": {"type": "boolean", "default": False}
                    },
                    "required": ["index_name"]
                }
            ),
            Tool(
                name="get_table_ddl",
                description="Generate CREATE TABLE statement for an existing table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Table name"},
                        "schema": {"type": "string", "default": "public"}
                    },
                    "required": ["table_name"]
                }
            ),
            
            # Data Manipulation Tools (DML)
            Tool(
                name="insert_data",
                description="Insert a row into a table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Table name"},
                        "data": {"type": "object", "description": "Column:value pairs"},
                        "schema": {"type": "string", "default": "public"}
                    },
                    "required": ["table_name", "data"]
                }
            ),
            Tool(
                name="bulk_insert",
                description="Insert multiple rows into a table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Table name"},
                        "data_list": {"type": "array", "description": "List of rows to insert"},
                        "schema": {"type": "string", "default": "public"}
                    },
                    "required": ["table_name", "data_list"]
                }
            ),
            Tool(
                name="update_data",
                description="Update rows in a table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Table name"},
                        "data": {"type": "object", "description": "Column:value pairs to update"},
                        "where_clause": {"type": "string", "description": "WHERE clause (without WHERE keyword)"},
                        "where_params": {"type": "array", "description": "Parameters for WHERE clause"},
                        "schema": {"type": "string", "default": "public"}
                    },
                    "required": ["table_name", "data", "where_clause"]
                }
            ),
            Tool(
                name="delete_data",
                description="Delete rows from a table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Table name"},
                        "where_clause": {"type": "string", "description": "WHERE clause (without WHERE keyword)"},
                        "where_params": {"type": "array", "description": "Parameters for WHERE clause"},
                        "schema": {"type": "string", "default": "public"}
                    },
                    "required": ["table_name", "where_clause"]
                }
            ),
            
            # User Management Tools (DCL)
            Tool(
                name="list_users",
                description="List all database users/roles",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="create_user",
                description="Create a new database user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "Username"},
                        "password": {"type": "string", "description": "Password (optional)"},
                        "can_login": {"type": "boolean", "default": True},
                        "can_create_db": {"type": "boolean", "default": False},
                        "can_create_role": {"type": "boolean", "default": False}
                    },
                    "required": ["username"]
                }
            ),
            Tool(
                name="grant_permissions",
                description="Grant permissions to a user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "Username"},
                        "privileges": {"type": "string", "description": "Privileges (e.g., SELECT, INSERT, ALL)"},
                        "object_type": {"type": "string", "description": "Object type (TABLE, DATABASE, SCHEMA)"},
                        "object_name": {"type": "string", "description": "Object name"},
                        "schema": {"type": "string", "default": "public"}
                    },
                    "required": ["username", "privileges", "object_type", "object_name"]
                }
            ),
            Tool(
                name="revoke_permissions",
                description="Revoke permissions from a user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "Username"},
                        "privileges": {"type": "string", "description": "Privileges to revoke"},
                        "object_type": {"type": "string", "description": "Object type"},
                        "object_name": {"type": "string", "description": "Object name"},
                        "schema": {"type": "string", "default": "public"}
                    },
                    "required": ["username", "privileges", "object_type", "object_name"]
                }
            ),
            Tool(
                name="list_permissions",
                description="List permissions for a user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "Username"}
                    },
                    "required": ["username"]
                }
            ),
            
            # Maintenance Tools
            Tool(
                name="vacuum_analyze",
                description="Run VACUUM ANALYZE on a table or database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Table name (optional, None for entire DB)"},
                        "schema": {"type": "string", "default": "public"},
                        "full": {"type": "boolean", "default": False}
                    }
                }
            ),
            Tool(
                name="backup_database",
                description="Create a database backup using pg_dump",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "output_file": {"type": "string", "description": "Output file path (optional)"},
                        "format": {"type": "string", "default": "custom", "enum": ["custom", "plain", "directory", "tar"]}
                    }
                }
            ),
            Tool(
                name="restore_database",
                description="Restore database from backup",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "backup_file": {"type": "string", "description": "Backup file path"},
                        "clean": {"type": "boolean", "default": False}
                    },
                    "required": ["backup_file"]
                }
            ),
            Tool(
                name="kill_connections",
                description="Terminate active connections to a database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "target_database": {"type": "string", "description": "Database name (optional)"}
                    }
                }
            ),
            Tool(
                name="get_active_connections",
                description="Get information about active database connections",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="test_connection",
                description="Test the database connection",
                inputSchema={"type": "object", "properties": {}}
            )
        ]
    
    async def call_tool(self, name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls."""
        try:
            # Ensure managers are initialized
            if not self.db:
                self.initialize_managers()
            
            # Route to appropriate handler
            result = None
            
            # Query Execution Tools
            if name == "execute_query":
                result = self.query_executor.execute_select_query(
                    arguments["query"],
                    tuple(arguments.get("params", []))
                )
            elif name == "execute_explain":
                result = self.query_executor.execute_explain(arguments["query"])
            elif name == "list_databases":
                result = self.query_executor.list_databases()
            elif name == "list_tables":
                result = self.query_executor.list_tables(arguments.get("schema", "public"))
            elif name == "list_columns":
                result = self.query_executor.list_columns(
                    arguments["table_name"],
                    arguments.get("schema", "public")
                )
            elif name == "get_table_info":
                result = self.query_executor.get_table_info(
                    arguments["table_name"],
                    arguments.get("schema", "public")
                )
            elif name == "get_database_size":
                result = self.query_executor.get_database_size()
            
            # Schema Management Tools
            elif name == "create_table":
                result = self.schema_manager.create_table(
                    arguments["table_name"],
                    arguments["columns"],
                    arguments.get("schema", "public")
                )
            elif name == "drop_table":
                result = self.schema_manager.drop_table(
                    arguments["table_name"],
                    arguments.get("schema", "public"),
                    arguments.get("cascade", False)
                )
            elif name == "alter_table":
                result = self.schema_manager.alter_table(
                    arguments["table_name"],
                    arguments["action"],
                    arguments.get("schema", "public")
                )
            elif name == "create_index":
                result = self.schema_manager.create_index(
                    arguments["index_name"],
                    arguments["table_name"],
                    arguments["columns"],
                    arguments.get("schema", "public"),
                    arguments.get("unique", False)
                )
            elif name == "drop_index":
                result = self.schema_manager.drop_index(
                    arguments["index_name"],
                    arguments.get("schema", "public"),
                    arguments.get("cascade", False)
                )
            elif name == "get_table_ddl":
                result = self.schema_manager.get_table_ddl(
                    arguments["table_name"],
                    arguments.get("schema", "public")
                )
            
            # Data Manipulation Tools
            elif name == "insert_data":
                result = self.data_manager.insert_data(
                    arguments["table_name"],
                    arguments["data"],
                    arguments.get("schema", "public")
                )
            elif name == "bulk_insert":
                result = self.data_manager.bulk_insert(
                    arguments["table_name"],
                    arguments["data_list"],
                    arguments.get("schema", "public")
                )
            elif name == "update_data":
                result = self.data_manager.update_data(
                    arguments["table_name"],
                    arguments["data"],
                    arguments["where_clause"],
                    tuple(arguments.get("where_params", [])),
                    arguments.get("schema", "public")
                )
            elif name == "delete_data":
                result = self.data_manager.delete_data(
                    arguments["table_name"],
                    arguments["where_clause"],
                    tuple(arguments.get("where_params", [])),
                    arguments.get("schema", "public")
                )
            
            # User Management Tools
            elif name == "list_users":
                result = self.user_manager.list_users()
            elif name == "create_user":
                result = self.user_manager.create_user(
                    arguments["username"],
                    arguments.get("password"),
                    arguments.get("can_login", True),
                    arguments.get("can_create_db", False),
                    arguments.get("can_create_role", False)
                )
            elif name == "grant_permissions":
                result = self.user_manager.grant_permissions(
                    arguments["username"],
                    arguments["privileges"],
                    arguments["object_type"],
                    arguments["object_name"],
                    arguments.get("schema", "public")
                )
            elif name == "revoke_permissions":
                result = self.user_manager.revoke_permissions(
                    arguments["username"],
                    arguments["privileges"],
                    arguments["object_type"],
                    arguments["object_name"],
                    arguments.get("schema", "public")
                )
            elif name == "list_permissions":
                result = self.user_manager.list_permissions(arguments["username"])
            
            # Maintenance Tools
            elif name == "vacuum_analyze":
                result = self.maintenance_manager.vacuum_analyze(
                    arguments.get("table_name"),
                    arguments.get("schema", "public"),
                    arguments.get("full", False)
                )
            elif name == "backup_database":
                result = self.maintenance_manager.backup_database(
                    arguments.get("output_file"),
                    arguments.get("format", "custom")
                )
            elif name == "restore_database":
                result = self.maintenance_manager.restore_database(
                    arguments["backup_file"],
                    arguments.get("clean", False)
                )
            elif name == "kill_connections":
                result = self.maintenance_manager.kill_connections(
                    arguments.get("target_database")
                )
            elif name == "get_active_connections":
                result = self.maintenance_manager.get_active_connections()
            elif name == "test_connection":
                result = self.db.test_connection()
            else:
                result = {"success": False, "error": f"Unknown tool: {name}"}
            
            # Format response
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}", exc_info=True)
            error_result = {"success": False, "error": str(e)}
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point for the PostgreSQL MCP server."""
    logger.info("Starting PostgreSQL MCP Server...")
    server = PostgreSQLMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()

