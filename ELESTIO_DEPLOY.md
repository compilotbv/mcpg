# Deploying PostgreSQL MCP Server on Elestio

Step-by-step guide for deploying to Elestio.

## Prerequisites

- Elestio account
- PostgreSQL database (can be on Elestio or elsewhere)
- Git repository with this code

## Step 1: Prepare Environment

Generate a secure API key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Save this key - you'll need it for both Elestio and Cursor config.

## Step 2: Deploy on Elestio

### Option A: Using Docker Compose

1. Create new service on Elestio
2. Choose "Docker Compose" template
3. Upload your `docker-compose.yml`
4. Configure environment variables in Elestio dashboard:

```env
MCP_API_KEY=your_generated_api_key
POSTGRES_HOST=your_postgres_host
POSTGRES_PORT=5432
POSTGRES_DB=your_database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
```

5. Deploy

### Option B: Using Dockerfile

1. Create new service → Custom Docker
2. Point to your Git repository
3. Set environment variables
4. Set exposed port: 8080
5. Deploy

## Step 3: Note Your URLs

After deployment, Elestio provides:
- Public URL: `https://your-service.elestio.app`
- Port: 8080 (mapped automatically)

## Step 4: Configure Cursor IDE

Update your Cursor MCP settings:

**Location:** 
- macOS: `~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json`
- Linux: `~/.config/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json`
- Windows: `%APPDATA%\Cursor\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json`

**Configuration:**

```json
{
  "mcpServers": {
    "postgresql": {
      "url": "https://your-service.elestio.app:8080",
      "headers": {
        "Authorization": "Bearer your_generated_api_key"
      }
    }
  }
}
```

## Step 5: Test Connection

```bash
# Test health endpoint
curl https://your-service.elestio.app:8080/health

# Test authentication
curl -H "Authorization: Bearer your_api_key" \
  https://your-service.elestio.app:8080/tools

# Test a tool
curl -X POST \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT version()"}' \
  https://your-service.elestio.app:8080/tools/execute_query
```

## Step 6: Use in Cursor

Restart Cursor and start using natural language:

- "Show me all tables"
- "What's the structure of the users table?"
- "List all databases"

## Security Best Practices for Elestio

1. **Use strong API key** - 32+ random characters
2. **Enable HTTPS** - Elestio provides SSL by default
3. **Restrict CORS** - Set `CORS_ORIGINS` to your domain only
4. **Use read-only PostgreSQL user** for safer queries
5. **Set POSTGRES_READONLY=true** for exploration
6. **Use PostgreSQL SSL** - Set `POSTGRES_SSLMODE=require`
7. **Monitor logs** - Check Elestio logs regularly

## Troubleshooting

### Connection Refused

- Check service is running in Elestio dashboard
- Verify port 8080 is exposed
- Check firewall rules

### Authentication Failed

- Verify API key matches in both .env and Cursor config
- Check Authorization header format: `Bearer <key>`

### Database Connection Failed

- Verify PostgreSQL credentials
- Check PostgreSQL allows connections from Elestio IP
- Test with: `curl https://your-service.elestio.app:8080/health`

### CORS Errors

- Set `CORS_ORIGINS=https://cursor.sh,https://cursor.com`
- Or use `*` for development (not recommended for production)

## Updating the Deployment

```bash
# Push changes to git
git push origin main

# In Elestio dashboard:
# 1. Go to your service
# 2. Click "Rebuild"
# Or enable auto-deploy on git push
```

## Monitoring

Check logs in Elestio dashboard:
- Application logs
- Error logs
- Access logs

Set up alerts for:
- Service downtime
- High error rates
- Failed authentication attempts

## Cost Optimization

- Use connection pooling (already configured)
- Set appropriate `POSTGRES_POOL_MAX`
- Monitor and optimize query performance
- Use read replicas for heavy read workloads

