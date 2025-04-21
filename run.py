import os
import subprocess
import sys

# Directorio del frontend
frontend_dir = os.path.join("agente_literario_ui", "frontend")
# Comando para ejecutar el frontend
# Primero intenta con el npm local, luego con el npm global
if os.path.exists(os.path.join(frontend_dir, "node_modules", ".bin", "npm")):
    frontend_command = [os.path.join(frontend_dir, "node_modules", ".bin", "npm"), "run", "dev"]
else:
    # Si npm no se encuentra en node_modules/.bin, intenta con npm.cmd
    # Busca npm en el PATH
    npm_path = None
    for path in os.environ["PATH"].split(os.pathsep):
        npm_cmd = os.path.join(path, "npm.cmd")
        if os.path.exists(npm_cmd):
            npm_path = npm_cmd
            break
    if npm_path:
        frontend_command = [npm_path, "run", "dev"]
    else:
        print("npm no encontrado en node_modules/.bin/ ni en el PATH.")
        sys.exit(1)

print("Ejecutando el frontend en {}...".format(frontend_dir))
try:
    frontend_process = subprocess.Popen(frontend_command, cwd=frontend_dir)
    # frontend_process.wait() # Eliminar la espera

except FileNotFoundError:
    # Si npm.cmd no se encuentra, asume que npm está en el PATH
    print("npm no encontrado en node_modules/.bin/. Intentando con npm.cmd")
    frontend_command = ["npm", "run", "dev"]
    frontend_process = subprocess.Popen(frontend_command, cwd=frontend_dir)
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
