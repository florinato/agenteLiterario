# communication.py
import re

import logging_manager  # Importar logging_manager


# Funciones para crear mensajes etiquetados
def create_respuesta_usuario(message: str) -> str:
    """Formato para la respuesta final al usuario."""
    return f"respuesta_usuario: {message}"

def create_respuesta_sistema(output: str) -> str:
    """Formato genérico para la respuesta del sistema tras ejecutar una acción."""
    return f"respuesta_sistema: {output}"

# Función para parsear mensajes
def parse_message(message: str):
    """
    Parsea un mensaje buscando la *última* aparición del patrón 'etiqueta: contenido'.
    Las etiquetas esperadas son 'execute_command', 'tool_call', 'respuesta_sistema', 'respuesta_usuario'.
    Esto maneja casos donde el modelo añade texto introductorio antes de la etiqueta final.
    Si no se encuentra un patrón válido, devuelve (None, message) usando el mensaje original para logs.
    """
    logging_manager.log_debug("Communication", f"Mensaje completo del modelo: {message}")  # Log del mensaje completo del modelo
    # Lista de etiquetas válidas (en minúsculas para comparación insensible al caso)
    valid_labels = ["execute_command", "tool_call", "respuesta_sistema", "respuesta_usuario"]
    best_match = None
    last_pos = -1

    # Buscar la última ocurrencia de cualquier etiqueta válida seguida de ':'
    for label in valid_labels:
        # Usar re.finditer para encontrar todas las ocurrencias (ignorando caso)
        # Buscamos la etiqueta seguida de ':' con espacios opcionales alrededor
        pattern = re.compile(r"(\b" + re.escape(label) + r"\b\s*:)", re.IGNORECASE | re.DOTALL)
        for match in pattern.finditer(message):
            start_pos = match.start(1)  # Posición de inicio de la etiqueta + ':'
            if start_pos > last_pos:
                last_pos = start_pos
                # Extraer la etiqueta encontrada (normalizada) y el contenido después de ella
                found_label = label  # Ya está en minúsculas
                # El contenido empieza después del grupo capturado (etiqueta + ':')
                content_start = match.end(1)
                content = message[content_start:].strip()
                best_match = (found_label, content)

    if best_match:
        # Se encontró al menos una etiqueta válida, devolver la última encontrada
        return best_match
    else:
        # No se encontró ninguna etiqueta válida en todo el mensaje
        # Devolver None y el mensaje original para los logs
        return None, message
