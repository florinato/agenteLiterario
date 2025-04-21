import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Define the path to the 'historias' directory relative to the main project root
# backend/main.py adds the project root (agenteLiterario) to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
HISTORIAS_DIR = os.path.join(PROJECT_ROOT, 'historias')

class FileSystemItem(BaseModel):
    name: str
    path: str # Relative path from HISTORIAS_DIR
    is_directory: bool
    children: Optional[List['FileSystemItem']] = None # For recursive listing if needed later

@router.get("/list", response_model=List[FileSystemItem])
async def list_files(path: Optional[str] = None):
    """
    Lists files and directories within the 'historias' directory or a specified subdirectory.
    Currently lists only the top level of the requested path.
    """
    if not os.path.exists(HISTORIAS_DIR) or not os.path.isdir(HISTORIAS_DIR):
        raise HTTPException(status_code=404, detail=f"'historias' directory not found at {HISTORIAS_DIR}")

    current_path = HISTORIAS_DIR
    relative_base_path = ""

    if path:
        # Prevent path traversal attacks
        requested_path = os.path.abspath(os.path.join(HISTORIAS_DIR, path))
        if not requested_path.startswith(os.path.abspath(HISTORIAS_DIR)):
             raise HTTPException(status_code=400, detail="Invalid path specified (attempted traversal).")
        if not os.path.exists(requested_path) or not os.path.isdir(requested_path):
            raise HTTPException(status_code=404, detail=f"Subdirectory not found: {path}")
        current_path = requested_path
        relative_base_path = path

    items = []
    try:
        for item_name in os.listdir(current_path):
            item_full_path = os.path.join(current_path, item_name)
            item_relative_path = os.path.join(relative_base_path, item_name).replace('\\', '/') # Use forward slashes for consistency
            is_directory = os.path.isdir(item_full_path)
            # Optionally filter for specific file types, e.g., only .md
            # if not is_directory and not item_name.lower().endswith('.md'):
            #     continue
            items.append(FileSystemItem(
                name=item_name,
                path=item_relative_path,
                is_directory=is_directory
            ))
        # Sort items alphabetically, directories first
        items.sort(key=lambda x: (not x.is_directory, x.name.lower()))
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Error reading directory {current_path}: {e}")

    return items

class FileContent(BaseModel):
    path: str
    content: str

@router.get("/read", response_model=FileContent)
async def read_file(path: str):
    """Reads the content of a specific file within the 'historias' directory."""
    if not path:
        raise HTTPException(status_code=400, detail="File path parameter is required.")

    # Basic security check: ensure path doesn't try to escape HISTORIAS_DIR
    target_path = os.path.join(HISTORIAS_DIR, path)

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    if not os.path.isfile(target_path):
        raise HTTPException(status_code=400, detail=f"Path is not a file: {path}")

    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return FileContent(path=path, content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file {path}: {e}")

class SaveFileRequest(BaseModel):
    path: str
    content: str

@router.post("/save")
async def save_file(file_data: SaveFileRequest):
    """Saves the content to a specific file within the 'historias' directory."""
    if not file_data.path:
        raise HTTPException(status_code=400, detail="File path parameter is required.")

    # Basic security check: ensure path doesn't try to escape HISTORIAS_DIR
    target_path = os.path.join(HISTORIAS_DIR, file_data.path)
    if not target_path.startswith(HISTORIAS_DIR):
        raise HTTPException(status_code=400, detail="Invalid path specified (attempted traversal).")

    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(file_data.content)
        return {"message": f"File saved successfully to {file_data.path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file {file_data.path}: {e}")

class RenameFileRequest(BaseModel):
    oldPath: str
    newPath: str

@router.post("/rename")
async def rename_file(rename_data: RenameFileRequest):
    """Renames a file or directory within the 'historias' directory."""
    if not rename_data.oldPath or not rename_data.newPath:
        raise HTTPException(status_code=400, detail="Old and new file paths are required.")

    old_path = os.path.join(HISTORIAS_DIR, rename_data.oldPath)
    new_path = os.path.join(HISTORIAS_DIR, rename_data.newPath)

    # Security checks to prevent path traversal
    if not old_path.startswith(HISTORIAS_DIR) or \
       not new_path.startswith(HISTORIAS_DIR):
        raise HTTPException(status_code=400, detail="Invalid path specified (attempted traversal).")

    if not os.path.exists(old_path):
        raise HTTPException(status_code=404, detail=f"File not found: {rename_data.oldPath}")

    try:
        os.rename(old_path, new_path)
        return {"message": f"Renamed '{rename_data.oldPath}' to '{rename_data.newPath}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error renaming file: {e}")

class DeleteFileRequest(BaseModel):
    path: str

@router.delete("/delete")
async def delete_file(path: str):
    """Deletes a file or directory within the 'historias' directory."""
    if not path:
        raise HTTPException(status_code=400, detail="File path parameter is required.")

    target_path = os.path.join(HISTORIAS_DIR, path)

    # Security checks to prevent path traversal
    if not target_path.startswith(HISTORIAS_DIR):
        raise HTTPException(status_code=400, detail="Invalid path specified (attempted traversal).")

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    try:
        if os.path.isfile(target_path):
            os.remove(target_path)
        elif os.path.isdir(target_path):
            os.rmdir(target_path)  # For now, only allow deleting empty directories
        else:
            raise HTTPException(status_code=400, detail=f"Path is not a file or directory: {path}")

        return {"message": f"Deleted '{path}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")

class CreateFileRequest(BaseModel):
    path: str
    content: str = ""

@router.post("/create")
async def create_file(file_data: CreateFileRequest):
    """Creates a new file within the 'historias' directory."""
    if not file_data.path:
        raise HTTPException(status_code=400, detail="File path parameter is required.")

    target_path = os.path.join(HISTORIAS_DIR, file_data.path)

    # Security checks to prevent path traversal
    if not target_path.startswith(HISTORIAS_DIR):
        raise HTTPException(status_code=400, detail="Invalid path specified (attempted traversal).")

    if os.path.exists(target_path):
        raise HTTPException(status_code=400, detail=f"File already exists: {file_data.path}")

    try:
        if file_data.content == "" and not os.path.isdir(target_path):
            # Create an empty file
            open(target_path, 'a').close()
        else:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(file_data.content)
        return {"message": f"File created successfully at {file_data.path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating file {file_data.path}: {e}")

@router.post("/create_directory")
async def create_directory(path: str):
    """Creates a new directory within the 'historias' directory."""
    target_path = os.path.join(HISTORIAS_DIR, path)

    # Security checks to prevent path traversal
    if not target_path.startswith(HISTORIAS_DIR):
        raise HTTPException(status_code=400, detail="Invalid path specified (attempted traversal).")

    if os.path.exists(target_path):
        raise HTTPException(status_code=400, detail=f"Directory already exists: {path}")

    try:
        os.makedirs(target_path)
        return {"message": f"Directory created successfully at {path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating directory {path}: {e}")
