# 🚀 Railway Deployment Guide

## What Has Been Set Up

Your gpt-engineer repository is now configured for Railway deployment with:

1. **FastAPI Web Server** (`server.py`) - A production-ready REST API
2. **Web Interface** (`static/index.html`) - Interactive UI for testing
3. **Railway Configuration** (`railway.toml`, `nixpacks.toml`, `Procfile`)
4. **Updated Dependencies** (`pyproject.toml`) - Added FastAPI and Uvicorn

## 🎯 Preview Status

✅ **Server is running locally on port 8000**
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 📋 Pre-Deployment Checklist

Before committing to Railway, ensure:

- [ ] You have an OpenAI API key ready
- [ ] You've tested the local preview
- [ ] You're happy with the API endpoints
- [ ] You understand the cost implications (OpenAI API usage)

## 🚂 Deploy to Railway

### Step 1: Connect to Railway

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Choose "Deploy from GitHub repo"
5. Select this repository (`gpt-engineer`)

### Step 2: Configure Environment Variables

In Railway project settings, add:

**Required:**
```
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

**Optional:**
```
MODEL_NAME=gpt-4o
```

For Anthropic Claude models:
```
ANTHROPIC_API_KEY=your-anthropic-key
```

### Step 3: Deploy

Railway will automatically:
1. Detect the Python project
2. Install dependencies via Poetry
3. Start the server with `python server.py`
4. Assign a public URL

### Step 4: Access Your API

After deployment, Railway provides a URL like:
```
https://your-project-name.up.railway.app
```

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
curl https://your-railway-url.railway.app/health
```

### 2. Generate Code
```bash
curl -X POST https://your-railway-url.railway.app/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a Python CLI calculator",
    "model": "gpt-4o"
  }'
```

### 3. Web Interface
Visit your Railway URL in a browser to use the interactive UI.

## 📊 API Endpoints Reference

### `GET /`
Web interface (HTML)

### `GET /health`
Health check for monitoring

### `POST /generate`
Generate code from a prompt

**Request:**
```json
{
  "prompt": "Create a Flask API for user management",
  "model": "gpt-4o",
  "temperature": 0.1,
  "project_name": "user-api"
}
```

**Response:**
```json
{
  "project_id": "user-api_20250113_120000",
  "status": "completed",
  "created_at": "2025-01-13T12:00:00",
  "files": ["app.py", "requirements.txt", "README.md"]
}
```

### `GET /project/{project_id}`
Get project information

### `GET /project/{project_id}/files`
Get all files and their contents

### `GET /project/{project_id}/download/{filepath}`
Download a specific file

### `GET /projects`
List all generated projects

### `DELETE /project/{project_id}`
Delete a project

## 💰 Cost Considerations

- Each code generation request uses OpenAI API credits
- Costs depend on:
  - Model used (GPT-4o is more expensive than GPT-3.5)
  - Prompt complexity
  - Generated code length
- Railway charges for compute time (generous free tier available)

## 🔒 Security Best Practices

1. **Never commit your `.env` file** - Use Railway's environment variables
2. **Rotate API keys regularly** - Change them periodically
3. **Monitor usage** - Check OpenAI dashboard for usage patterns
4. **Rate limiting** - Consider adding rate limiting in production
5. **Authentication** - Add API authentication for production use

## 🐛 Troubleshooting

### Server Won't Start
- Check Railway logs: Click on your service → Logs
- Verify `OPENAI_API_KEY` is set correctly
- Ensure all dependencies installed (Railway handles this)

### API Requests Failing
- Check OpenAI API key is valid and has credits
- Verify model name is correct
- Check Railway service logs for errors

### Slow Generation
- Normal - AI generation takes 30-60 seconds for complex projects
- Use simpler prompts for faster results
- Consider GPT-3.5-turbo for speed vs GPT-4o for quality

## 📈 Monitoring

Railway provides:
- Real-time logs
- Resource usage metrics
- Request metrics
- Error tracking

Access via: Project → Service → Metrics

## 🔄 Updates and Maintenance

### To Update the API:
1. Make changes locally
2. Test with `python server.py`
3. Commit and push to GitHub
4. Railway auto-deploys from your main branch

### To Rollback:
- Railway → Deployments → Select previous deployment → Redeploy

## 🌐 Custom Domain (Optional)

Railway allows custom domains:
1. Railway project → Settings → Domains
2. Add your domain
3. Configure DNS records as shown

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [GPT Engineer GitHub](https://github.com/gpt-engineer-org/gpt-engineer)

## 🆘 Support

- **Railway Issues**: [Railway Discord](https://discord.gg/railway)
- **GPT Engineer Issues**: [GitHub Issues](https://github.com/gpt-engineer-org/gpt-engineer/issues)
- **API Problems**: Check logs and verify API keys

## 🎉 You're All Set!

Your API is ready to deploy. When you're satisfied with the local preview:

```bash
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

Then connect to Railway and watch it deploy! 🚀
