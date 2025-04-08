# security.py
import logging_manager

# NOTE: The is_action_dangerous function is removed as the security check
# is now handled by the agent (LLM) asking for confirmation before generating
# dangerous commands, or by the 'execute_command' tool's 'requires_approval' flag.

def request_authorization() -> bool:
    """
    Solicita confirmación al usuario para ejecutar una acción peligrosa.
    Devuelve True si el usuario confirma, False en caso contrario.
    NOTE: This function is not currently called by the main loop in main.py
    after the refactoring, but kept in case it's needed elsewhere.
    """
    while True:
        try:
            response = input("Esta acción requiere confirmación. ¿Desea continuar? (s/n): ").lower().strip()
            if response == 's':
                logging_manager.log_debug("Security Auth", "User authorized action.")
                return True
            elif response == 'n':
                logging_manager.log_debug("Security Auth", "User denied action.")
                return False
            else:
                print("Respuesta no válida. Por favor, ingrese 's' para sí o 'n' para no.")
        except EOFError:
            # Handle cases where input stream might be closed unexpectedly
            logging_manager.log_warning("Security Auth", "EOFError received during authorization request. Assuming denial.")
            print("\nEntrada no disponible. Asumiendo 'no'.")
            return False
