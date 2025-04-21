import os
import shutil
import subprocess

import communication
import logging_manager

HISTORIAS_DIR = os.getenv("HISTORIAS_DIR")

def replace_backslashes(ruta):
    return ruta.replace("\\", "/")

def handle_command(command):
    logging_manager.logging.debug("Executor - handle_command", "Comando recibido: {}".format(command))
    if command.startswith("leer"):
        return leer_historia(command)
    elif command.startswith("listar"):
        return listar_directorio(command)
    elif command.startswith("buscar"):
        return buscar_en_archivo(command)
    else:
        return "❌ Comando no reconocido"

def leer_historia(command):
    logging_manager.logging.debug("Executor - leer_historia", "Comando recibido: {}".format(command))
    try:
        partes = command.split(" ", 1)
        if len(partes) < 1:
            return "❌ Comando 'leer' incompleto. Debe especificar la ruta del archivo."
        _, ruta = partes
        ruta_procesada = replace_backslashes(ruta.strip())
        ruta_norm = os.path.normpath(ruta_procesada)
        ruta_abs = os.path.join(HISTORIAS_DIR, ruta_norm)
        if os.access(ruta_abs, os.R_OK):
            with open(ruta_abs, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return f"❌ No tiene permisos de lectura en: {ruta_abs}"
    except Exception as e:
        return f"❌ Error al leer la historia: {e}"

def listar_directorio(command):
    logging_manager.logging.debug("Executor - listar_directorio", "Comando recibido: {}".format(command))
    try:
        partes = command.split(" ", 1)
        if len(partes) < 1:
            return "❌ Comando 'listar' incompleto. Debe especificar la ruta del directorio."
        _, ruta = partes
        ruta_abs = os.path.join(HISTORIAS_DIR, ruta.strip())
        if os.path.isdir(ruta_abs) and os.access(ruta_abs, os.R_OK):
            archivos = os.listdir(ruta_abs)
            logging_manager.logging.debug("Executor - listar_directorio", "Archivos encontrados: {}".format(archivos)) # Add logging
            return "\\n".join(archivos)
        else:
            return f"❌ No es un directorio o no tiene permisos de lectura en: {ruta_abs}"
    except Exception as e:
        return f"❌ Error al listar el directorio: {e}"



def buscar_en_archivo(command):
    logging_manager.logging.debug("Executor - buscar_en_archivo", "Comando recibido: {}".format(command))
    try:
        partes = command.split(" ", 2)
        if len(partes) < 2:
            return "❌ Comando 'buscar' incompleto. Debe especificar la ruta del archivo y el texto a buscar."
        _, ruta = partes
        ruta_abs = os.path.join(HISTORIAS_DIR, ruta.strip())
        #texto = texto.strip('"')
        texto = partes[1].strip('"')
        if os.access(ruta_abs, os.R_OK):
            try:
                with open(ruta_abs, "r", encoding="utf-8") as f:
                    contenido = f.read()
                    if texto in contenido:
                        return f"✅ Se encontró '{{texto}}' en {ruta_abs}"
                    else:
                        return f"❌ No se encontró '{{texto}}' en {ruta_abs}"
            except Exception as e:
                return f"❌ Error al buscar en el archivo: {e}"
        else:
            return f"❌ No tiene permisos de lectura en: {ruta_abs}"
    except Exception as e:
        return f"❌ Error al procesar la búsqueda: {e}"

import communication
