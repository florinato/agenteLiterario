import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the backend directory to the Python path
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Add the parent directory (agenteLiterario) to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import agente_literario_ui.backend.logging_manager as logging_manager

logging_manager.log_debug("Backend", "Backend application started")

# Add the parent directory (agenteLiterario) to the Python path
# This allows importing modules like executor, model_integration, etc.
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# TODO: Import agent modules when needed
# from executor import execute_agent_command
# from communication import get_file_list, read_file_content, save_file_content

# --- FastAPI App Setup ---
app = FastAPI(
    title="Agente Literario UI Backend",
    description="API endpoints to interact with the Agente Literario and manage story files.",
    version="0.1.0",
)

# --- CORS Middleware ---
# Allow requests from the frontend development server (adjust origins as needed)
origins = [
    "http://localhost:3000",  # Default for create-react-app
    "http://localhost:5173",  # Default for Vite
    # Add other origins if your frontend runs on a different port/domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- API Routers ---
from api import agent, files

app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])


# --- Root Endpoint ---
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Agente Literario UI Backend!"}

# --- Placeholder Endpoints (to be moved to routers) ---

@app.get("/api/placeholder")
async def placeholder():
    # Example of accessing parent directory modules (if needed later)
    # try:
    #     # Replace with actual function call when implemented
    #     # data = some_function_from_parent_module()
    #     data = {"info": "Placeholder data"}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    return {"message": "API is running. Implement specific endpoints in api/."}


# --- Run Instructions (for development) ---
# To run the backend server:
# 1. Navigate to the 'agente_literario_ui/backend' directory in your terminal.
# 2. Ensure you have a virtual environment activated with the dependencies installed (pip install -r requirements.txt).
# 3. Run: uvicorn main:app --reload
