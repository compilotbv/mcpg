# PostgreSQL MCP Server

Model Context Protocol server for PostgreSQL with HTTP/SSE transport for remote deployment. Built with Python, FastAPI, and Docker for Elestio or any cloud platform.

## Features

- **HTTP/SSE Transport**: Remote access via HTTPS
- **API Key Authentication**: Secure access control
- **Query Execution**: Execute SELECT queries with natural language
- **Schema Management**: Create, alter, and drop tables and indexes
- **Data Manipulation**: Insert, update, and delete data
- **User Management**: Create users and manage permissions
- **Database Maintenance**: VACUUM, backups, and connection management
- **Secure**: Read-only mode, connection pooling, and query timeouts

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t postgresql-mcp-server .
```

### 2. Configure Environment

Generate API key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
# Edit .env with your PostgreSQL and API key
```

### 3. Run with Docker Compose

```bash
docker-compose up -d
```

Server will be available at `http://localhost:8080`

### 4. Configure Cursor IDE

Add to Cursor MCP settings:

```json
{
  "mcpServers": {
    "postgresql": {
      "url": "https://your-server.com:8080",
      "headers": {
        "Authorization": "Bearer your_api_key"
      }
    }
  }
}
```

See [ELESTIO_DEPLOY.md](ELESTIO_DEPLOY.md) for deployment guide.

## Available Tools

### Query Tools
- `execute_query` - Run SELECT queries
- `execute_explain` - Get query execution plans
- `list_databases` - List all databases
- `list_tables` - List tables in schema
- `list_columns` - Show column information
- `get_table_info` - Get detailed table metadata
- `get_database_size` - Get database and table sizes

### Schema Management (DDL)
- `create_table` - Create new tables
- `drop_table` - Remove tables
- `alter_table` - Modify table structure
- `create_index` - Create indexes
- `drop_index` - Remove indexes
- `get_table_ddl` - Generate CREATE TABLE statements

### Data Operations (DML)
- `insert_data` - Insert single row
- `bulk_insert` - Insert multiple rows
- `update_data` - Update rows
- `delete_data` - Delete rows

### User Management (DCL)
- `list_users` - List database users
- `create_user` - Create new users
- `grant_permissions` - Grant privileges
- `revoke_permissions` - Revoke privileges
- `list_permissions` - Show user permissions

### Maintenance
- `vacuum_analyze` - Run VACUUM ANALYZE
- `backup_database` - Create pg_dump backup
- `restore_database` - Restore from backup
- `kill_connections` - Terminate connections
- `get_active_connections` - Show active connections
- `test_connection` - Test database connection

## Usage Examples

Once configured in Cursor, interact with your database naturally:

```
"Show me all tables in the database"
"What's the structure of the users table?"
"Find the top 10 customers by order count"
"Create a products table with id, name, and price columns"
"Insert a new user with email test@example.com"
"Show me all database users and their permissions"
```

## Configuration Options

Environment variables:

- `POSTGRES_HOST` - Database host (default: localhost)
- `POSTGRES_PORT` - Database port (default: 5432)
- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_READONLY` - Read-only mode (default: false)
- `POSTGRES_SSLMODE` - SSL mode (default: prefer)
- `POSTGRES_POOL_MIN` - Min connections (default: 1)
- `POSTGRES_POOL_MAX` - Max connections (default: 10)
- `QUERY_TIMEOUT` - Query timeout in seconds (default: 30)

## Security Best Practices

1. **Use environment variables** for credentials, never hardcode
2. **Enable read-only mode** for exploration: `POSTGRES_READONLY=true`
3. **Create dedicated users** with minimal required privileges
4. **Use SSL connections** for production: `POSTGRES_SSLMODE=require`
5. **Set query timeouts** to prevent long-running queries
6. **Limit connection pools** based on your database capacity

## Deployment Options

### Option 1: Using Docker Compose (Recommended)

Edit `.env` with your PostgreSQL credentials:

```bash
docker-compose up -d
```

### Option 2: Direct Docker Run

```bash
docker run -i --rm \
  -e POSTGRES_HOST=your_host \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_DB=your_db \
  -e POSTGRES_USER=your_user \
  -e POSTGRES_PASSWORD=your_password \
  postgresql-mcp-server
```

## Project Structure

```
mcpg/
├── src/postgresql_mcp_server/
│   ├── __init__.py
│   ├── server.py              # Main MCP server
│   ├── db_manager.py           # Connection management
│   ├── query_executor.py       # Query execution
│   ├── schema_manager.py       # DDL operations
│   ├── data_manager.py         # DML operations
│   ├── user_manager.py         # User management
│   └── maintenance_manager.py  # Maintenance tools
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── cursor-mcp-config.json
├── CURSOR_SETUP.md
└── README.md
```

## Troubleshooting

### Connection Issues

1. Verify PostgreSQL is accessible:
   ```bash
   docker run -it --rm postgres:16-alpine psql -h host.docker.internal -U user -d db
   ```

2. Check Docker network settings for container-to-container communication

3. Review Cursor logs for MCP errors

### Permission Errors

- Verify database user has required privileges
- Check PostgreSQL pg_hba.conf for access rules
- Use `test_connection` tool to diagnose

### Docker Issues

- Ensure Docker daemon is running
- Check for port conflicts (5432)
- Verify image is built: `docker images | grep postgresql-mcp-server`

## Development

### Requirements

- Python 3.11+
- PostgreSQL 12+
- Docker 20.10+

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
# ... other vars

# Run directly
python -m src.postgresql_mcp_server.server
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or PR.

## Support

For issues and questions:
- Check [CURSOR_SETUP.md](CURSOR_SETUP.md) for setup help
- Review [Troubleshooting](#troubleshooting) section
- Open a GitHub issue

## Additional Documentation

- [Cursor Setup Guide](CURSOR_SETUP.md) - Detailed Cursor IDE integration
- [MCP Protocol](https://modelcontextprotocol.io/) - MCP specification
- [PostgreSQL Docs](https://www.postgresql.org/docs/) - PostgreSQL documentation


