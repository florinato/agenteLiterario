import os
import subprocess
import sys

# Directorio del frontend
frontend_dir = os.path.join("agente_literario_ui", "frontend")
# Comando para ejecutar el frontend
frontend_command = ["npm", "run", "dev"]

print("Ejecutando el frontend en {}...".format(frontend_dir))
frontend_process = subprocess.Popen(frontend_command, cwd=frontend_dir, shell=True)
    # frontend_process.wait() # Eliminar la espera

# Comando y directorio para ejecutar el backend
backend_dir = os.path.join("agente_literario_ui", "backend")
backend_command = ["uvicorn", "main:app", "--reload"]

print("Ejecutando el backend en {}...".format(backend_dir))
try:
    backend_process = subprocess.Popen(backend_command, cwd=backend_dir, shell=True)
except FileNotFoundError as e:
    print(f"Error al ejecutar el backend: {e}")
    sys.exit(1)

print("Frontend y backend ejecutándose en terminales separadas.")
