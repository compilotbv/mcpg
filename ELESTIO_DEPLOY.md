# Deploying PostgreSQL MCP Server on Elestio

Complete guide for deploying to Elestio using Custom docker-compose template.

## Prerequisites

- Elestio account ([signup here](https://elest.io))
- Docker Hub account (or other registry)
- PostgreSQL database credentials

## Step 1: Build and Push Docker Image

```bash
# Build the image
docker build -t your-dockerhub-username/postgresql-mcp-server:latest .

# Login to Docker Hub
docker login

# Push to registry
docker push your-dockerhub-username/postgresql-mcp-server:latest
```

## Step 2: Generate API Key

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Save this key for Step 4.

## Step 3: Deploy on Elestio

1. **Go to CI/CD** from left sidebar
2. **Select "Docker compose"** as deployment source
3. **Choose "Custom docker-compose"** template
4. **Click Deploy** button

## Step 4: Choose Deployment Target

### Option A: Deploy on New VM
- Select cloud provider (AWS, DigitalOcean, Vultr, Linode, Hetzner)
- Choose region
- Select service plan
- Name your target

### Option B: Deploy on Existing VM
- Select existing CI/CD target from dropdown

Click **Next**

## Step 5: Configure Docker Image

### Docker Image Settings:

**Docker Compose Content:**
Paste your `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgresql-mcp-server:
    image: your-dockerhub-username/postgresql-mcp-server:latest
    container_name: postgresql-mcp-server
    ports:
      - "3000:3000"
    environment:
      MCP_HOST: 0.0.0.0
      MCP_PORT: 3000
      MCP_API_KEY: ${MCP_API_KEY}
      CORS_ORIGINS: ${CORS_ORIGINS}
      POSTGRES_HOST: ${POSTGRES_HOST}
      POSTGRES_PORT: ${POSTGRES_PORT}
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_READONLY: ${POSTGRES_READONLY}
      POSTGRES_SSLMODE: ${POSTGRES_SSLMODE}
      POSTGRES_POOL_MIN: ${POSTGRES_POOL_MIN}
      POSTGRES_POOL_MAX: ${POSTGRES_POOL_MAX}
      QUERY_TIMEOUT: ${QUERY_TIMEOUT}
    restart: unless-stopped
```

**If using private registry:**
- ☑ Check "Use a private Docker registry"
- Enter registry URL, username, password

## Step 6: Configure Environment Variables

Add all ENV variables in the Elestio UI:

### Required Variables:
```
MCP_API_KEY=your_generated_api_key_from_step_2
POSTGRES_HOST=your_postgres_host
POSTGRES_PORT=5432
POSTGRES_DB=your_database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
```

### Optional Variables:
```
CORS_ORIGINS=*
POSTGRES_READONLY=false
POSTGRES_SSLMODE=prefer
POSTGRES_POOL_MIN=1
POSTGRES_POOL_MAX=10
QUERY_TIMEOUT=30
```

## Step 7: Configure Reverse Proxy

In the "Reverse Proxy Settings" section:

- **Port**: `3000`
- **Protocol**: HTTPS (Elestio provides SSL automatically)

Pipeline name will auto-fill, customize if needed.

## Step 8: Create Pipeline

Click **"Create CI/CD pipeline"**

Elestio will:
- Deploy your container
- Configure reverse proxy
- Set up SSL certificate
- Provide you with public URL

## Step 9: Get Your Service URL

After deployment (2-3 minutes):

1. Go to your pipeline dashboard
2. Note the public URL: `https://your-service-xxxxx.elestio.app`
3. Test health endpoint:

```bash
curl https://your-service-xxxxx.elestio.app/health
```

## Step 10: Configure Cursor IDE

Update Cursor MCP settings:

**macOS:** `~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json`

**Linux:** `~/.config/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json`

**Windows:** `%APPDATA%\Cursor\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "postgresql": {
      "url": "https://your-service-xxxxx.elestio.app",
      "headers": {
        "Authorization": "Bearer your_api_key_from_step_2"
      }
    }
  }
}
```

## Step 11: Test in Cursor

Restart Cursor and try:
- "Show me all tables"
- "What's the structure of the users table?"
- "List all databases"

## Testing Your Deployment

### Test Endpoints

```bash
# Health check
curl https://your-service.elestio.app/health

# List tools (requires auth)
curl -H "Authorization: Bearer your_api_key" \
  https://your-service.elestio.app/tools

# Execute query
curl -X POST \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT version()"}' \
  https://your-service.elestio.app/tools/execute_query
```

## Updating Your Deployment

### Method 1: Push New Image

```bash
# Build new version
docker build -t your-dockerhub-username/postgresql-mcp-server:latest .

# Push to registry
docker push your-dockerhub-username/postgresql-mcp-server:latest

# In Elestio dashboard: Restart pipeline to pull new image
```

### Method 2: Update docker-compose.yml

1. Go to your pipeline in Elestio
2. Edit configuration
3. Update docker-compose content
4. Save and redeploy

## Troubleshooting

### Service Won't Start

**Check logs in Elestio:**
1. Go to pipeline dashboard
2. Click "Logs"
3. Look for errors

**Common issues:**
- Missing ENV variables
- Wrong PostgreSQL credentials
- Port conflicts

### Can't Connect from Cursor

**Verify:**
1. Service is running: `curl https://your-service.elestio.app/health`
2. API key matches in both Elestio ENV and Cursor config
3. Authorization header format: `Bearer <key>` (note the space)

### Database Connection Failed

**Check:**
1. PostgreSQL allows external connections
2. Firewall allows Elestio IP
3. Credentials are correct
4. Test with health endpoint

### Authentication Errors

**Common causes:**
1. API key mismatch
2. Missing "Bearer " prefix
3. Extra spaces in key
4. Key not set in ENV variables

## Security Best Practices

1. **Use strong API key** (32+ characters)
2. **Restrict CORS** - Set `CORS_ORIGINS` to your domain only
3. **Use PostgreSQL SSL** - Set `POSTGRES_SSLMODE=require`
4. **Read-only mode** - Set `POSTGRES_READONLY=true` for queries
5. **Monitor access logs** in Elestio dashboard
6. **Rotate API keys** regularly
7. **Use private Docker registry** for proprietary code

## Cost Optimization

- Choose appropriate VM size for your load
- Use connection pooling (already configured)
- Set `POSTGRES_POOL_MAX` based on your DB limits
- Monitor resource usage in Elestio dashboard
- Scale up/down as needed

## Support

- **Elestio Support**: support@elest.io or ticketing system
- **Elestio Discord**: [Join here](https://discord.gg/elestio)
- **Documentation**: https://docs.elest.io

## Additional Resources

- [Elestio Custom docker-compose Guide](https://docs.elest.io/books/cicd-pipelines/page/deploy-own-docker-compose-image-using-elestio-custom-docker-compose)
- [Elestio CI/CD Overview](https://docs.elest.io/books/cicd-pipelines)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
