# GPT Engineer - Railway Deployment

This repository is configured for deployment on Railway with a FastAPI web server wrapper.

## Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

## Setup Instructions

### 1. Environment Variables

Set the following environment variable in your Railway project:

- `OPENAI_API_KEY` - Your OpenAI API key (required)

Optional variables:
- `ANTHROPIC_API_KEY` - For using Claude models
- `MODEL_NAME` - Default model to use (default: `gpt-4o`)
- `PORT` - Server port (Railway sets this automatically)

### 2. Local Development

To test the server locally before deploying:

```bash
# Install dependencies
poetry install

# Set your API key
export OPENAI_API_KEY=your_key_here

# Run the server
python server.py
```

The server will start on `http://localhost:8000`

### 3. API Endpoints

Once deployed, your API will have these endpoints:

#### `GET /` - API Information
Returns service information and available endpoints.

#### `GET /health` - Health Check
For Railway health monitoring.

#### `POST /generate` - Generate Code
Generate code from a natural language prompt.

**Request Body:**
```json
{
  "prompt": "Create a Python Flask REST API for a todo list",
  "model": "gpt-4o",
  "temperature": 0.1,
  "project_name": "my-todo-api"
}
```

**Response:**
```json
{
  "project_id": "my-todo-api_20250113_120000",
  "status": "completed",
  "created_at": "2025-01-13T12:00:00",
  "files": ["app.py", "requirements.txt", "README.md"]
}
```

#### `GET /project/{project_id}` - Get Project Status
Get information about a generated project.

#### `GET /project/{project_id}/files` - Get All Files
Get the content of all files in a project.

#### `GET /project/{project_id}/download/{filepath}` - Download File
Download a specific file from a project.

#### `GET /projects` - List All Projects
List all generated projects.

#### `DELETE /project/{project_id}` - Delete Project
Delete a project and its files.

## Testing the API

### Using cURL

```bash
# Generate code
curl -X POST https://your-railway-app.railway.app/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a simple Python calculator with add, subtract, multiply, and divide functions",
    "model": "gpt-4o"
  }'

# Get project files
curl https://your-railway-app.railway.app/project/{project_id}/files
```

### Using Python

```python
import requests

# Generate code
response = requests.post(
    "https://your-railway-app.railway.app/generate",
    json={
        "prompt": "Create a simple Python calculator",
        "model": "gpt-4o"
    }
)
project = response.json()
print(f"Project ID: {project['project_id']}")

# Get generated files
files_response = requests.get(
    f"https://your-railway-app.railway.app/project/{project['project_id']}/files"
)
files = files_response.json()
for filename, content in files.items():
    print(f"\n--- {filename} ---\n{content}")
```

## Features

- **AI Code Generation**: Generate complete projects from natural language descriptions
- **Multiple Models**: Support for OpenAI (GPT-4, GPT-3.5) and Anthropic (Claude) models
- **Project Management**: Store, retrieve, and manage generated projects
- **File Access**: Download individual files or get all project files at once
- **RESTful API**: Simple HTTP endpoints for easy integration

## Architecture

The application consists of:
- **FastAPI Server** (`server.py`): Web API wrapper around gpt-engineer
- **GPT Engineer Core**: Original CLI tool for AI code generation
- **Railway Configuration**: Deployment files for Railway platform

## Troubleshooting

### Server won't start
- Check that `OPENAI_API_KEY` is set in Railway environment variables
- Check Railway logs for detailed error messages

### Generation fails
- Verify your API key has sufficient credits
- Check the model name is correct
- Review the prompt for clarity

### Files not found
- Projects are stored temporarily and may be cleaned up
- Use the `/projects` endpoint to see available projects

## Local CLI Usage

The original CLI tool is still available:

```bash
poetry shell
gpte projects/my-project
```

See the main [README.md](README.md) for full CLI documentation.

## Support

For issues with:
- **Railway deployment**: Check [Railway docs](https://docs.railway.app)
- **GPT Engineer**: See [main repository](https://github.com/gpt-engineer-org/gpt-engineer)
- **API usage**: Check `/` endpoint for API documentation

## License

MIT License - see [LICENSE](LICENSE) file for details.
