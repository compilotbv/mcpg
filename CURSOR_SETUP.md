# Cursor IDE Setup for PostgreSQL MCP Server

This guide explains how to integrate the PostgreSQL MCP Server with Cursor IDE.

## Prerequisites

1. Docker installed and running
2. PostgreSQL database accessible from your machine
3. Cursor IDE installed

## Setup Steps

### 1. Build the Docker Image

First, build the PostgreSQL MCP Server Docker image:

```bash
cd /home/peter/mcpg
docker build -t postgresql-mcp-server .
```

### 2. Configure Cursor IDE

Cursor uses an MCP configuration file to connect to MCP servers. You need to add the PostgreSQL MCP server configuration to your Cursor settings.

#### Location of Config File

The MCP configuration file location depends on your operating system:

- **macOS**: `~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json`
- **Linux**: `~/.config/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json`
- **Windows**: `%APPDATA%\Cursor\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json`

#### Configuration Options

There are two ways to configure the server:

##### Option 1: Using Environment Variables (Recommended for Security)

Create a `.env` file in your project with your credentials:

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
```

Then add this to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "postgresql": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--name",
        "postgresql-mcp-server",
        "--env-file",
        "/absolute/path/to/your/.env",
        "postgresql-mcp-server"
      ]
    }
  }
}
```

##### Option 2: Direct Configuration (Simple but Less Secure)

Add this configuration directly to your Cursor MCP settings file:

```json
{
  "mcpServers": {
    "postgresql": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--name",
        "postgresql-mcp-server",
        "-e",
        "POSTGRES_HOST=host.docker.internal",
        "-e",
        "POSTGRES_PORT=5432",
        "-e",
        "POSTGRES_DB=your_database",
        "-e",
        "POSTGRES_USER=your_user",
        "-e",
        "POSTGRES_PASSWORD=your_password",
        "postgresql-mcp-server"
      ]
    }
  }
}
```

**Important Notes:**
- Replace `your_database`, `your_user`, and `your_password` with your actual credentials
- Use `host.docker.internal` as the host when connecting to a database on your local machine
- If your PostgreSQL is in another Docker container, use the container name or Docker network

### 3. Network Configuration

#### Connecting to Local PostgreSQL (on host machine)

Use `host.docker.internal` as the `POSTGRES_HOST`:

```json
"-e", "POSTGRES_HOST=host.docker.internal"
```

#### Connecting to PostgreSQL in Another Docker Container

If your PostgreSQL is running in another Docker container, connect both to the same network:

```bash
# Create a Docker network (if not exists)
docker network create pg-network

# Connect your existing PostgreSQL container to the network
docker network connect pg-network your-postgres-container

# Update docker-compose.yml to use the network
```

Add to `docker-compose.yml`:

```yaml
services:
  postgresql-mcp-server:
    networks:
      - pg-network
    environment:
      - POSTGRES_HOST=your-postgres-container

networks:
  pg-network:
    external: true
```

### 4. Test the Connection

1. Restart Cursor IDE
2. Open the MCP panel (usually accessible via the sidebar)
3. You should see "postgresql" listed as an available MCP server
4. Try a natural language query like: "Show me all tables in the database"

## Usage Examples

Once configured, you can interact with your PostgreSQL database using natural language:

### Basic Queries

- "List all tables in the public schema"
- "Show me the structure of the users table"
- "What are the top 10 customers by revenue?"
- "Explain the query: SELECT * FROM orders WHERE created_at > '2024-01-01'"

### Schema Management

- "Create a table called products with columns id, name, and price"
- "Add an index on the email column in the users table"
- "Show me the DDL for the orders table"

### Data Operations

- "Insert a new user with email 'test@example.com' and name 'Test User'"
- "Update the status to 'completed' for order_id 123"
- "Delete all records from the temp_data table where created_at is older than 30 days"

### Administration

- "Show me all database users and their permissions"
- "What's the size of the database?"
- "Show active database connections"
- "Run VACUUM ANALYZE on the large_table"

## Troubleshooting

### Connection Issues

If you can't connect to PostgreSQL:

1. **Check Docker is running**: `docker ps`
2. **Verify PostgreSQL is accessible**: `docker run -it --rm postgres:16-alpine psql -h host.docker.internal -U your_user -d your_db`
3. **Check Cursor logs**: Look for MCP-related errors in Cursor's developer console

### Permission Errors

If you get permission errors:

- Ensure the PostgreSQL user has appropriate privileges
- For read-only access, set `POSTGRES_READONLY=true` in the environment variables

### Tool Not Found

If the MCP server doesn't appear in Cursor:

- Restart Cursor IDE completely
- Check the MCP settings file is in the correct location
- Verify the JSON configuration is valid

## Security Best Practices

1. **Never commit credentials**: Add `.env` to `.gitignore`
2. **Use read-only mode for exploration**: Set `POSTGRES_READONLY=true`
3. **Create dedicated database users**: Don't use superuser accounts
4. **Use SSL connections**: Set `POSTGRES_SSLMODE=require` for production databases
5. **Limit connection pools**: Set appropriate `POSTGRES_POOL_MAX` values

## Advanced Configuration

### Read-Only Mode

For safer operations, enable read-only mode:

```json
"-e", "POSTGRES_READONLY=true"
```

### Connection Pooling

Adjust connection pool settings:

```json
"-e", "POSTGRES_POOL_MIN=1",
"-e", "POSTGRES_POOL_MAX=5"
```

### Query Timeout

Set a query timeout (in seconds):

```json
"-e", "QUERY_TIMEOUT=30"
```

## Additional Resources

- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Networking Guide](https://docs.docker.com/network/)


