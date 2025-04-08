import os
import subprocess

# Directorios
frontend_dir = "agente_literario_ui/frontend"
backend_dir = "agente_literario_ui/backend"

# Comandos
frontend_command = ["npm", "run", "dev"]
backend_command = ["uvicorn", "main:app", "--reload"]

# Cambiar al directorio del frontend y ejecutar el comando
print(f"Ejecutando el frontend en {frontend_dir}...")
frontend_process = subprocess.Popen(frontend_command, cwd=frontend_dir, shell=True)

# Cambiar al directorio del backend y ejecutar el comando
print(f"Ejecutando el backend en {backend_dir}...")
backend_process = subprocess.Popen(backend_command, cwd=backend_dir)

# Esperar a que terminen los procesos (opcional)
frontend_process.wait()
backend_process.wait()

print("Frontend y backend finalizados.")
