#!/bin/bash

# Ejecutar el frontend
cd agente_literario_ui/frontend
npm run dev &

# Ejecutar el backend
cd ../backend
uvicorn main:app --reload
