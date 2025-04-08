# logging_manager.py
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler  # Added import

LOG_FILE = "mongo_agent.log"

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# Configurar logging a la consola
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(console_handler)

# Ajustar nivel para librerías que pueden exponer información sensible
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Set up rotating file handler
log_handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5) # 10MB max size, 5 backups
log_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(log_handler)

def add_log(entry: str):
    """Agrega una entrada de conversación (INFO) al archivo de log."""
    logging.info(entry)

def log_debug(label: str, data: str):
    """Agrega una entrada de depuración (DEBUG) al archivo de log."""
    # Formatear datos multilínea para mejor legibilidad
    formatted_data = data.replace('\n', '\n' + ' ' * (len(label) + 12)) # Indentar líneas siguientes
    logging.debug(f"[{label}]: {formatted_data}")

def log_warning(label: str):
    """Agrega una entrada de advertencia (WARNING) al archivo de log."""
    logging.warning(f"[{label}]")

def log_error(label: str, exc_info=False):
    """Agrega una entrada de error (ERROR) al archivo de log."""
    logging.error(f"[{label}]", exc_info=exc_info)


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

# Limpiar el log al inicio de cada ejecución.
try:
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        print(f"Log anterior ({LOG_FILE}) eliminado.") # Mensaje informativo
except Exception as e:
    print(f"Advertencia: No se pudo limpiar el log anterior ({LOG_FILE}): {e}")
