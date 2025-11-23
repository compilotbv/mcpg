# PostgreSQL MCP Server - Usage Guide

Complete reference for all available tools and their usage.

## Query Tools

### execute_query

Execute SELECT queries with results.

**Example prompts:**
- "Show me all users"
- "Get the top 10 orders by amount"
- "Find customers who signed up in the last month"

**Direct usage:**
```json
{
  "name": "execute_query",
  "arguments": {
    "query": "SELECT * FROM users WHERE created_at > $1",
    "params": ["2024-01-01"]
  }
}
```

### execute_explain

Get query execution plan.

**Example prompts:**
- "Explain this query: SELECT * FROM large_table WHERE status = 'active'"
- "Show me the execution plan for finding all active users"

### list_databases

List all accessible databases.

**Example prompts:**
- "Show me all databases"
- "What databases are available?"

### list_tables

List tables in a schema.

**Example prompts:**
- "Show all tables in the public schema"
- "List tables"

**Direct usage:**
```json
{
  "name": "list_tables",
  "arguments": {
    "schema": "public"
  }
}
```

### list_columns

Show column information for a table.

**Example prompts:**
- "Show me the structure of the users table"
- "What columns does the orders table have?"

### get_table_info

Get detailed table metadata including indexes and constraints.

**Example prompts:**
- "Tell me everything about the products table"
- "Show detailed information for the orders table"

### get_database_size

Get database and table sizes.

**Example prompts:**
- "How large is the database?"
- "Show me the size of all tables"

## Schema Management Tools (DDL)

### create_table

Create new tables.

**Example prompts:**
- "Create a products table with id, name VARCHAR(200), price DECIMAL, and created_at TIMESTAMP"
- "Make a new table called categories with an id and name"

**Direct usage:**
```json
{
  "name": "create_table",
  "arguments": {
    "table_name": "products",
    "columns": [
      {"name": "id", "type": "SERIAL", "constraints": "PRIMARY KEY"},
      {"name": "name", "type": "VARCHAR(200)", "constraints": "NOT NULL"},
      {"name": "price", "type": "DECIMAL(10,2)", "constraints": ""},
      {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT NOW()"}
    ],
    "schema": "public"
  }
}
```

### drop_table

Remove tables.

**Example prompts:**
- "Drop the temp_data table"
- "Remove the old_users table with cascade"

### alter_table

Modify table structure.

**Example prompts:**
- "Add a status column to the orders table"
- "Alter the users table to add a last_login timestamp column"

**Direct usage:**
```json
{
  "name": "alter_table",
  "arguments": {
    "table_name": "orders",
    "action": "ADD COLUMN status VARCHAR(50) DEFAULT 'pending'",
    "schema": "public"
  }
}
```

### create_index

Create indexes.

**Example prompts:**
- "Create an index on the email column in users table"
- "Add a unique index on username in the users table"

**Direct usage:**
```json
{
  "name": "create_index",
  "arguments": {
    "index_name": "idx_users_email",
    "table_name": "users",
    "columns": ["email"],
    "unique": false,
    "schema": "public"
  }
}
```

### drop_index

Remove indexes.

**Example prompts:**
- "Drop the idx_users_email index"

### get_table_ddl

Generate CREATE TABLE statement.

**Example prompts:**
- "Show me the DDL for the users table"
- "Generate CREATE TABLE statement for products"

## Data Manipulation Tools (DML)

### insert_data

Insert a single row.

**Example prompts:**
- "Insert a new user with email test@example.com and name Test User"
- "Add a product called Widget with price 19.99"

**Direct usage:**
```json
{
  "name": "insert_data",
  "arguments": {
    "table_name": "users",
    "data": {
      "email": "test@example.com",
      "name": "Test User",
      "created_at": "2024-01-15"
    },
    "schema": "public"
  }
}
```

### bulk_insert

Insert multiple rows.

**Example prompts:**
- "Insert these three users: ..."
- "Bulk insert data into products table"

**Direct usage:**
```json
{
  "name": "bulk_insert",
  "arguments": {
    "table_name": "products",
    "data_list": [
      {"name": "Product A", "price": 10.99},
      {"name": "Product B", "price": 20.99},
      {"name": "Product C", "price": 15.99}
    ],
    "schema": "public"
  }
}
```

### update_data

Update rows.

**Example prompts:**
- "Update the status to 'completed' for order 123"
- "Set all users with email ending in @oldomain.com to inactive"

**Direct usage:**
```json
{
  "name": "update_data",
  "arguments": {
    "table_name": "orders",
    "data": {
      "status": "completed",
      "updated_at": "2024-01-15"
    },
    "where_clause": "id = %s",
    "where_params": [123],
    "schema": "public"
  }
}
```

### delete_data

Delete rows.

**Example prompts:**
- "Delete all records from temp_table older than 30 days"
- "Remove the user with id 456"

**Direct usage:**
```json
{
  "name": "delete_data",
  "arguments": {
    "table_name": "temp_data",
    "where_clause": "created_at < NOW() - INTERVAL '30 days'",
    "where_params": [],
    "schema": "public"
  }
}
```

## User Management Tools (DCL)

### list_users

List all database users/roles.

**Example prompts:**
- "Show me all database users"
- "List all roles"

### create_user

Create new database user.

**Example prompts:**
- "Create a readonly user called report_viewer"
- "Make a new user named api_user with login ability"

**Direct usage:**
```json
{
  "name": "create_user",
  "arguments": {
    "username": "report_viewer",
    "password": "secure_password",
    "can_login": true,
    "can_create_db": false,
    "can_create_role": false
  }
}
```

### grant_permissions

Grant privileges.

**Example prompts:**
- "Grant SELECT on all tables in public schema to report_viewer"
- "Give INSERT and UPDATE permissions on orders table to api_user"

**Direct usage:**
```json
{
  "name": "grant_permissions",
  "arguments": {
    "username": "report_viewer",
    "privileges": "SELECT",
    "object_type": "TABLE",
    "object_name": "orders",
    "schema": "public"
  }
}
```

### revoke_permissions

Revoke privileges.

**Example prompts:**
- "Revoke DELETE on products table from api_user"

### list_permissions

Show user permissions.

**Example prompts:**
- "What permissions does report_viewer have?"
- "Show all privileges for api_user"

## Maintenance Tools

### vacuum_analyze

Run VACUUM ANALYZE.

**Example prompts:**
- "Run VACUUM ANALYZE on the orders table"
- "Optimize the entire database"

**Direct usage:**
```json
{
  "name": "vacuum_analyze",
  "arguments": {
    "table_name": "orders",
    "schema": "public",
    "full": false
  }
}
```

### backup_database

Create database backup.

**Example prompts:**
- "Backup the database"
- "Create a backup in custom format"

**Direct usage:**
```json
{
  "name": "backup_database",
  "arguments": {
    "output_file": "/tmp/mydb_backup.dump",
    "format": "custom"
  }
}
```

### restore_database

Restore from backup.

**Example prompts:**
- "Restore the database from /tmp/backup.dump"

**Direct usage:**
```json
{
  "name": "restore_database",
  "arguments": {
    "backup_file": "/tmp/backup.dump",
    "clean": false
  }
}
```

### kill_connections

Terminate active connections.

**Example prompts:**
- "Kill all connections to testdb"
- "Terminate active connections"

### get_active_connections

Show active connections.

**Example prompts:**
- "Show me all active database connections"
- "What connections are currently open?"

### test_connection

Test database connection.

**Example prompts:**
- "Test the database connection"
- "Check if we're connected to the database"

## Tips for Natural Language Queries

1. **Be specific**: "Show users created after January 1, 2024" is better than "show some users"

2. **Use table names**: "from the orders table" helps identify the correct table

3. **Specify conditions clearly**: "where status is active" or "with price greater than 100"

4. **For complex operations**: Break into steps or be very explicit

5. **Check before modifying**: Use SELECT queries first to verify what will be affected

## Common Patterns

### Analysis Queries

```
"Show me the top 10 customers by total order value"
"How many users signed up each month in 2024?"
"What's the average order value by product category?"
```

### Schema Exploration

```
"Show me all tables"
"What's the structure of the users table?"
"Show indexes on the orders table"
```

### Data Modifications

```
"Insert a new order for user 123 with total 99.99"
"Update all pending orders to processing if created more than 1 hour ago"
"Delete test users where email contains 'test'"
```

### Maintenance

```
"Show database size"
"What's the size of the largest tables?"
"Show active connections"
"Run VACUUM ANALYZE on large_table"
```


