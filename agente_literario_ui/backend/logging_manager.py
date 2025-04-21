# logging_manager.py
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

LOG_FILE = "mongo_agent.log"

# Configure logging handlers
if not logging.getLogger().hasHandlers():
    # Configure basic logging
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )

    # Add rotating file handler
    log_handler = RotatingFileHandler(LOG_FILE, maxBytes=100*1024*1024, backupCount=10)
    log_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(log_handler)

# Configure logging to handle Unicode characters
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
    encoding="utf-8"  # Ensure Unicode characters are handled
)

# Almacena el último mensaje de log
last_log_message = None

# Filter for similar consecutive messages
def _is_last_log_similar(new_entry: str) -> bool:
    global last_log_message
    if last_log_message:
        # Comparar solo el mensaje después del nivel de log
        new_message = new_entry.split(" - ", 2)[-1]
        last_message = last_log_message.split(" - ", 2)[-1]
        if last_message == new_message:
            return True
    return False

# Adjust levels for sensitive libraries
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

def add_log(entry: str):
    """Agrega una entrada de conversación (INFO) al archivo de log."""
    global last_log_message
    if not _is_last_log_similar(entry):
        logging.info(entry)
        last_log_message = entry

def log_debug(label: str, data: str):
    """Agrega una entrada de depuración (DEBUG) al archivo de log, omitiendo el prompt inicial y duplicados."""
    global last_log_message
    # Omitir el log del prompt inicial completo
    if label == "Prompt Completo Enviado a API":
        return
    # Formatear datos multilínea para mejor legibilidad
    formatted_data = data.replace('\n', '\n' + ' ' * (len(label) + 12)) # Indentar líneas siguientes
    log_entry = f"[{label}]: {formatted_data}"
    if not _is_last_log_similar(log_entry):
        logging.debug(log_entry)
        last_log_message = log_entry

def log_warning(label: str):
    """Agrega una entrada de advertencia (WARNING) al archivo de log, omitiendo duplicados."""
    global last_log_message
    log_entry = f"WARNING: [{label}]"
    if not _is_last_log_similar(log_entry):
        logging.warning(log_entry)
        last_log_message = log_entry

def log_error(label: str, data: str, exc_info=False):
    """Agrega una entrada de error (ERROR) al archivo de log, omitiendo duplicados."""
    global last_log_message
    log_entry = f"ERROR: [{label}]: {data}"
    if not _is_last_log_similar(log_entry):
        logging.error(log_entry, exc_info=exc_info)
        last_log_message = log_entry


def get_log() -> str:
    """Devuelve el log completo como una cadena de texto desde el archivo."""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return "El archivo de log aún no existe."
    except Exception as e:
        print(f"Error al leer el log: {e}")
        return f"Error al leer el log: {e}"

def print_log():
    """Indica la ubicación del archivo de log."""
    print(f"El log completo se encuentra en: {os.path.abspath(LOG_FILE)}")
