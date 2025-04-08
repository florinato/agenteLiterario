# executor.py
import os
import subprocess
from os import getcwd

import logging_manager

# No fixed target directory anymore. Commands run in the project's root directory by default.

def execute_action(label: str, content: str) -> str:
    """
    Executes the action based on the label. Currently only handles 'execute_command'.
    Runs the command directly in PowerShell from the project's root directory.
    """
    if label == "execute_command":
        # Treat content directly as the PowerShell command, just strip whitespace
        command_to_execute = content.strip()
        try:
            logging_manager.log_debug("Executor", f"Intentando ejecutar comando: {command_to_execute}")
            # Execute the command explicitly using PowerShell from the current working directory
            # We pass the command string to PowerShell's -Command argument.
            # shell=False is generally safer when we control the executable.
            powershell_executable = "C:\\Program Files\\PowerShell\\7\\pwsh.exe" # Assumes PowerShell 7+ is in PATH
            try:
                # Capture raw bytes, do not decode automatically
                result = subprocess.run(
                    [powershell_executable, "-Command", command_to_execute],
                    capture_output=True,    # Capture stdout/stderr as bytes
                    # cwd=TARGET_DIR, # Removed: Execute in the current working directory of the script
                    shell=False             # Do not use the default shell
                )
                logging_manager.log_debug("Executor", f"Comando ejecutado. Código de retorno: {result.returncode}")
            except FileNotFoundError:
                # Fallback to older powershell.exe if pwsh.exe is not found
                powershell_executable = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
                logging_manager.log_debug("Executor Info", "pwsh.exe not found, trying powershell.exe")
                try:
                    result = subprocess.run(
                        [powershell_executable, "-Command", command_to_execute],
                        capture_output=True, # cwd=TARGET_DIR, # Removed
                        shell=False # Capture raw bytes
                    )
                    logging_manager.log_debug("Executor", f"Comando ejecutado (powershell.exe). Código de retorno: {result.returncode}")
                except FileNotFoundError:
                    error_msg = "Error: Ni 'pwsh.exe' ni 'powershell.exe' se encontraron en el PATH. No se puede ejecutar el comando PowerShell."
                    logging_manager.log_debug("Executor Error", error_msg)
                    return error_msg

            # --- Decode Output Bytes Robustly ---
            output = ""
            try:
                # Try decoding stdout using UTF-8 first, then common Windows encodings
                stdout_decoded = result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # Try cp1252 (Windows Latin 1)
                    stdout_decoded = result.stdout.decode('cp1252', errors='replace')
                    logging_manager.log_debug("Executor Info", "Decoded stdout using cp1252")
                except Exception:
                     # Fallback: decode with replacement if other encodings fail
                     stdout_decoded = result.stdout.decode('utf-8', errors='replace')
                     logging_manager.log_debug("Executor Warning", "Could not reliably decode stdout, used UTF-8 with replacement.")

            try:
                 # Try decoding stderr using UTF-8 first, then common Windows encodings
                stderr_decoded = result.stderr.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # Try cp1252
                    stderr_decoded = result.stderr.decode('cp1252', errors='replace')
                    logging_manager.log_debug("Executor Info", "Decoded stderr using cp1252")
                except Exception:
                    # Fallback
                    stderr_decoded = result.stderr.decode('utf-8', errors='replace')
                    logging_manager.log_debug("Executor Warning", "Could not reliably decode stderr, used UTF-8 with replacement.")

            # Combine decoded stdout and stderr
            if stdout_decoded:
                output += f"Salida:\\n{stdout_decoded.strip()}\\n"
            if stderr_decoded:
                output += f"Errores:\\n{stderr_decoded.strip()}\\n"

            if not output.strip(): # Check if output is truly empty after decoding
                # Distinguish between successful execution with no output vs actual errors
                if result.returncode == 0:
                    output = "Comando ejecutado con éxito (sin salida)."
                else:
                    # If there was an error code but no stderr message, provide a generic error
                    output = f"Comando falló con código de retorno {result.returncode} (sin salida de error específica)."

            return output.strip()

        except FileNotFoundError as e:
            error_msg = f"Error: Comando no encontrado o ruta inválida: '{command_to_execute}'. Detalles: {e}"
            logging_manager.log_error("Executor Error", error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error inesperado ejecutando comando: {e}. Tipo: {type(e).__name__}"
            logging_manager.log_error("Executor Error", error_msg)
            return error_msg
# executor.py
import os
import subprocess

import logging_manager

# No fixed target directory anymore. Commands run in the project's root directory by default.

def execute_action(label: str, content: str) -> str:
    """
    Executes the action based on the label. Currently only handles 'execute_command'.
    Runs the command directly in PowerShell from the project's root directory.
    """
    if label == "execute_command":
        # Treat content directly as the PowerShell command, just strip whitespace
        command_to_execute = content.strip()
        try:
            # Execute the command explicitly using PowerShell from the current working directory
            # We pass the command string to PowerShell's -Command argument.
            # shell=False is generally safer when we control the executable.
            powershell_executable = "C:\\Program Files\\PowerShell\\7\\pwsh.exe" # Assumes PowerShell 7+ is in PATH
            try:
                # Capture raw bytes, do not decode automatically
                result = subprocess.run(
                    [powershell_executable, "-Command", command_to_execute],
                    capture_output=True,    # Capture stdout/stderr as bytes
                    # cwd=TARGET_DIR, # Removed: Execute in the current working directory of the script
                    shell=False             # Do not use the default shell
                )
            except FileNotFoundError:
                # Fallback to older powershell.exe if pwsh.exe is not found
                powershell_executable = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
                logging_manager.log_debug("Executor Info", "pwsh.exe not found, trying powershell.exe")
                try:
                    result = subprocess.run(
                        [powershell_executable, "-Command", command_to_execute],
                        capture_output=True, # cwd=TARGET_DIR, # Removed
                        shell=False # Capture raw bytes
                    )
                except FileNotFoundError:
                    error_msg = "Error: Ni 'pwsh.exe' ni 'powershell.exe' se encontraron en el PATH. No se puede ejecutar el comando PowerShell."
                    logging_manager.log_debug("Executor Error", error_msg)
                    return error_msg

            # --- Decode Output Bytes Robustly ---
            output = ""
            try:
                # Try decoding stdout using UTF-8 first, then common Windows encodings
                stdout_decoded = result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # Try cp1252 (Windows Latin 1)
                    stdout_decoded = result.stdout.decode('cp1252', errors='replace')
                    logging_manager.log_debug("Executor Info", "Decoded stdout using cp1252")
                except Exception:
                     # Fallback: decode with replacement if other encodings fail
                     stdout_decoded = result.stdout.decode('utf-8', errors='replace')
                     logging_manager.log_debug("Executor Warning", "Could not reliably decode stdout, used UTF-8 with replacement.")

            try:
                 # Try decoding stderr using UTF-8 first, then common Windows encodings
                stderr_decoded = result.stderr.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # Try cp1252
                    stderr_decoded = result.stderr.decode('cp1252', errors='replace')
                    logging_manager.log_debug("Executor Info", "Decoded stderr using cp1252")
                except Exception:
                    # Fallback
                    stderr_decoded = result.stderr.decode('utf-8', errors='replace')
                    logging_manager.log_debug("Executor Warning", "Could not reliably decode stderr, used UTF-8 with replacement.")

            # Combine decoded stdout and stderr
            if stdout_decoded:
                output += f"Salida:\\n{stdout_decoded.strip()}\\n"
            

            if not output.strip(): # Check if output is truly empty after decoding
                # Distinguish between successful execution with no output vs actual errors
                if result.returncode == 0:
                    output = "Comando ejecutado con éxito (sin salida)."
                else:
                    # If there was an error code but no stderr message, provide a generic error
                    output = f"Comando falló con código de retorno {result.returncode} (sin salida de error específica)."

            return output.strip()

        except FileNotFoundError as e:
            error_msg = f"Error: Comando no encontrado o ruta inválida: '{command_to_execute}'. Detalles: {e}"
            logging_manager.log_debug("Executor Error", error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error inesperado ejecutando comando: {e}"
            logging_manager.log_debug("Executor Error", error_msg)
            return error_msg

    # Handle tool_call or other labels if they were re-introduced,
    # but based on the plan, we only expect execute_command now.
    # elif label == "tool_call":
    #     return "Error: La ejecución de 'tool_call' ha sido eliminada de este executor."

    else:
        # Should not be reached if main.py calls correctly
        error_msg = f"Error interno del Executor: Etiqueta desconocida '{label}'."
        logging_manager.log_debug("Executor Error", error_msg)
        return error_msg
