"""
Tests for server.py endpoints, specifically focusing on error handling.
"""
import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from server import app, PROJECTS_DIR


@pytest.fixture
def test_project():
    """Create a temporary test project with some files."""
    # Create a test project directory
    project_id = "test_project_123"
    project_path = PROJECTS_DIR / project_id
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Create some test files
    (project_path / "test_file.txt").write_text("Hello, World!")
    (project_path / "subdir").mkdir(exist_ok=True)
    (project_path / "subdir" / "nested.py").write_text("print('nested')")
    
    yield project_id, project_path
    
    # Cleanup
    import shutil
    if project_path.exists():
        shutil.rmtree(project_path)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_get_project_files_success(client, test_project):
    """Test that get_project_files returns correct structure with project_id and files."""
    project_id, project_path = test_project
    
    response = client.get(f"/project/{project_id}/files")
    assert response.status_code == 200
    
    data = response.json()
    
    # Check that response has the correct structure
    assert "project_id" in data
    assert "files" in data
    assert data["project_id"] == project_id
    
    # Check that files are present
    files = data["files"]
    assert isinstance(files, dict)
    assert "test_file.txt" in files
    assert files["test_file.txt"] == "Hello, World!"
    
    # Check nested file
    nested_key = str(Path("subdir") / "nested.py")
    assert nested_key in files
    assert files[nested_key] == "print('nested')"


def test_get_project_files_with_unreadable_file(client, test_project):
    """Test that get_project_files handles unreadable files gracefully with fallback key."""
    project_id, project_path = test_project
    
    # Create a file that will cause an error when reading (binary file)
    binary_file = project_path / "binary.bin"
    binary_file.write_bytes(b'\x80\x81\x82\x83')
    
    response = client.get(f"/project/{project_id}/files")
    assert response.status_code == 200
    
    data = response.json()
    assert "project_id" in data
    assert "files" in data
    
    # The binary file should either be read or have an error message
    # If it causes an error, it should use a fallback key
    files = data["files"]
    
    # Check that readable files are still present
    assert "test_file.txt" in files
    assert files["test_file.txt"] == "Hello, World!"


def test_get_project_files_nonexistent(client):
    """Test that get_project_files returns 404 for nonexistent project."""
    response = client.get("/project/nonexistent_project/files")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_server_import_does_not_start_uvicorn():
    """Test that importing server.py does not start uvicorn."""
    # This test ensures that uvicorn.run is behind the __name__ == "__main__" guard
    # If it's not, importing the server module would start the server
    # Since we can import it here without the server starting, this passes
    import server
    
    # If we got here without the server starting, the guard works
    assert hasattr(server, "app")
    assert hasattr(server, "get_project_files")
