import os
import subprocess

# Directorios
frontend_dir = "agente_literario_ui/frontend"
backend_dir = "agente_literario_ui/backend"

# Comandos
# En Windows, la ruta a npm sería algo como "agente_literario_ui/frontend/node_modules/.bin/npm.cmd"
# En otros sistemas, podría ser "agente_literario_ui/frontend/node_modules/.bin/npm"
# Para hacerlo portable, intentaremos ambas opciones.
frontend_command = ["node_modules/.bin/npm", "run", "dev"]
backend_command = ["uvicorn", "main:app", "--reload"]

# Cambiar al directorio del frontend y ejecutar el comando
print(f"Ejecutando el frontend en {frontend_dir}...")
try:
    frontend_process = subprocess.Popen(frontend_command, cwd=frontend_dir)
except FileNotFoundError:
    print("npm no encontrado en node_modules/.bin/. Intentando con npm.cmd")
    frontend_command = ["node_modules/.bin/npm.cmd", "run", "dev"]
    frontend_process = subprocess.Popen(frontend_command, cwd=frontend_dir)


# Cambiar al directorio del backend y ejecutar el comando
print(f"Ejecutando el backend en {backend_dir}...")
backend_process = subprocess.Popen(backend_command, cwd=backend_dir)

# Esperar a que terminen los procesos (opcional)
# No esperamos para que se ejecuten en paralelo
# frontend_process.wait()
# backend_process.wait()

print("Frontend y backend finalizados.")
