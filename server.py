"""
Railway deployment server for gpt-engineer.
Provides a simple web API to interact with gpt-engineer.
"""
import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import json

from gpt_engineer.core.ai import AI
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_engineer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.core.prompt import Prompt
from gpt_engineer.applications.cli.cli_agent import CliAgent
from gpt_engineer.core.default.steps import gen_code, execute_entrypoint, improve_fn
from gpt_engineer.core.default.file_store import FileStore

app = FastAPI(
    title="GPT Engineer API",
    description="AI-powered code generation API",
    version="0.3.1"
)

# Mount static files if the directory exists
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Store for active projects
PROJECTS_DIR = Path(tempfile.gettempdir()) / "gpt_engineer_projects"
PROJECTS_DIR.mkdir(exist_ok=True)


class GenerateRequest(BaseModel):
    prompt: str
    model: str = "gpt-4o"
    temperature: float = 0.1
    project_name: Optional[str] = None


class ImproveRequest(BaseModel):
    project_id: str
    prompt: str
    model: str = "gpt-4o"
    temperature: float = 0.1


class ProjectStatus(BaseModel):
    project_id: str
    status: str
    created_at: str
    files: list[str] = []


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface"""
    static_index = Path(__file__).parent / "static" / "index.html"
    if static_index.exists():
        return FileResponse(static_index)
    
    # Fallback to JSON if no static file
    return {
        "service": "gpt-engineer",
        "status": "running",
        "version": "0.3.1",
        "endpoints": {
            "generate": "/generate",
            "improve": "/improve",
            "project": "/project/{project_id}",
            "files": "/project/{project_id}/files",
            "download": "/project/{project_id}/download/{filepath}"
        }
    }

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "service": "gpt-engineer",
        "status": "running",
        "version": "0.3.1",
        "endpoints": {
            "generate": "/generate",
            "improve": "/improve",
            "project": "/project/{project_id}",
            "files": "/project/{project_id}/files",
            "download": "/project/{project_id}/download/{filepath}"
        }
    }


@app.get("/health")
async def health():
    """Health check for Railway"""
    return {"status": "healthy"}


@app.post("/generate", response_model=ProjectStatus)
async def generate_code(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Generate code from a natural language prompt.
    
    Args:
        request: GenerateRequest with prompt and model settings
        
    Returns:
        ProjectStatus with project_id and generation details
    """
    # Validate API key
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY or ANTHROPIC_API_KEY must be set in environment"
        )
    
    try:
        # Create project directory
        project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if request.project_name:
            project_id = f"{request.project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        project_path = PROJECTS_DIR / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize AI
        ai = AI(
            model_name=request.model,
            temperature=request.temperature,
        )
        
        # Create prompt
        prompt = Prompt(request.prompt)
        
        # Set up agent
        preprompts_holder = PrepromptsHolder(PREPROMPTS_PATH)
        memory = DiskMemory(memory_path(str(project_path)))
        execution_env = DiskExecutionEnv()
        
        agent = CliAgent.with_default_config(
            memory,
            execution_env,
            ai=ai,
            code_gen_fn=gen_code,
            improve_fn=improve_fn,
            process_code_fn=execute_entrypoint,
            preprompts_holder=preprompts_holder,
        )
        
        # Generate code
        files_dict = agent.init(prompt)
        
        # Save files
        files = FileStore(str(project_path))
        files.push(files_dict)
        
        # Get list of generated files
        generated_files = [str(f.relative_to(project_path)) for f in project_path.rglob("*") if f.is_file()]
        
        return ProjectStatus(
            project_id=project_id,
            status="completed",
            created_at=datetime.now().isoformat(),
            files=generated_files
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/project/{project_id}", response_model=ProjectStatus)
async def get_project(project_id: str):
    """
    Get project status and list of files.
    
    Args:
        project_id: The project identifier
        
    Returns:
        ProjectStatus with project details
    """
    project_path = PROJECTS_DIR / project_id
    
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get list of files
    files = [str(f.relative_to(project_path)) for f in project_path.rglob("*") if f.is_file()]
    
    # Get creation time
    created_at = datetime.fromtimestamp(project_path.stat().st_ctime).isoformat()
    
    return ProjectStatus(
        project_id=project_id,
        status="completed",
        created_at=created_at,
        files=files
    )


@app.get("/project/{project_id}/files")
async def get_project_files(project_id: str):
    """
    Get all files content from a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dictionary of filename -> content
    """
    project_path = PROJECTS_DIR / project_id
    
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    files_content = {}
    for file_path in project_path.rglob("*"):
        if file_path.is_file():
            try:
                relative_path = str(file_path.relative_to(project_path))
                with open(file_path, 'r', encoding='utf-8') as f:
                    files_content[relative_path] = f.read()
            except Exception as e:
                files_content[relative_path] = f"Error reading file: {str(e)}"
    
    return files_content


@app.get("/project/{project_id}/download/{filepath:path}")
async def download_file(project_id: str, filepath: str):
    """
    Download a specific file from a project.
    
    Args:
        project_id: The project identifier
        filepath: Relative path to the file within the project
        
    Returns:
        File content
    """
    project_path = PROJECTS_DIR / project_id
    file_path = project_path / filepath
    
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Security check: ensure file is within project directory
    try:
        file_path.resolve().relative_to(project_path.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(file_path)


@app.delete("/project/{project_id}")
async def delete_project(project_id: str):
    """
    Delete a project and all its files.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Success message
    """
    project_path = PROJECTS_DIR / project_id
    
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        shutil.rmtree(project_path)
        return {"message": f"Project {project_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")


@app.get("/projects")
async def list_projects():
    """
    List all available projects.
    
    Returns:
        List of project IDs and their creation dates
    """
    projects = []
    for project_path in PROJECTS_DIR.iterdir():
        if project_path.is_dir():
            created_at = datetime.fromtimestamp(project_path.stat().st_ctime).isoformat()
            projects.append({
                "project_id": project_path.name,
                "created_at": created_at
            })
    
    return {"projects": projects}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
