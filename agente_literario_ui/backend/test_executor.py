import executor  # Asegúrate de que el archivo executor.py esté en el mismo directorio o en el PYTHONPATH


def test_executor_methods():
    # Define the test commands
    test_commands = {
        "leer_historia": "#accion: leer ReGenesis/capitulo1/trama.md",
        "listar_directorio": "#accion: listar ReGenesis/capitulo1",
        "mostrar_arbol": "#accion: arbol ReGenesis",
        "buscar_en_archivo": '#accion: buscar ReGenesis/capitulo1/trama.md "personajes"'
    }

    # Execute the methods and capture the output
    output = {}
    for method_name, command in test_commands.items():
        try:
            method = getattr(executor, method_name)
            output[method_name] = method(command)
        except Exception as e:
            output[method_name] = f"Error al ejecutar el método: {e}"

    # Format the output
    formatted_output = "\\n".join([f"{method_name}: {output[method_name]}" for method_name in test_commands])

    # Save the output to a file
    with open("executor.txt", "w", encoding="utf-8") as f:
        f.write(formatted_output)

if __name__ == "__main__":
    test_executor_methods()
import executor  # Asegúrate de que el archivo executor.py esté en el mismo directorio o en el PYTHONPATH


def test_executor_methods():
    """Ejecutar los métodos de executor.py y guardar la salida en un archivo."""
    
    # Define the test commands
    test_commands = {
        "leer_historia": "#accion: leer ReGenesis/capitulo1/trama.md",
        "listar_directorio": "#accion: listar ReGenesis/capitulo1",
        "mostrar_arbol": "#accion: arbol ReGenesis",
        "buscar_en_archivo": '#accion: buscar ReGenesis/capitulo1/trama.md "personajes"'
    }
    
    # Execute the methods and capture the output
    output = {}
    for method_name, command in test_commands.items():
        method = getattr(executor, method_name)
        output[method_name] = method(command)
    
    # Format the output
    formatted_output = "\\n".join([f"{method_name}: {result}" for method_name, result in output.items()])
    
    # Save the output to a file
    with open("executor.txt", "w", encoding="utf-8") as f:
        f.write(formatted_output)

if __name__ == "__main__":
    #unittest.main()
    test_executor_methods()
    # Define the test commands
    test_commands = {
        "leer_historia": "#accion: leer ReGenesis/capitulo1/trama.md",
        "listar_directorio": "#accion: listar ReGenesis/capitulo1",
        "mostrar_arbol": "#accion: arbol ReGenesis",
        "buscar_en_archivo": '#accion: buscar ReGenesis/capitulo1/trama.md "personajes"'
    }
    
    # Execute the methods and capture the output
    output = {}
    for method_name, command in test_commands.items():
        method = getattr(executor, method_name)
        output[method_name] = method(command)
    
    # Format the output
    formatted_output = "\\n".join([f"{method_name}: {result}" for method_name, result in output.items()])
    
    # Save the output to a file
    with open("executor.txt", "w", encoding="utf-8") as f:
        f.write(formatted_output)

if __name__ == "__main__":
    #unittest.main()
    test_executor_methods()
import os
import unittest
from unittest.mock import MagicMock, patch

import executor  # Asegúrate de que el archivo executor.py esté en el mismo directorio o en el PYTHONPATH


class TestExecutor(unittest.TestCase):

    def setUp(self):
        """Configurar variables comunes para las pruebas."""
        self.base_dir = executor.HISTORIAS_DIR
        self.test_dir = os.path.join(self.base_dir, "test_dir")
        self.test_file = os.path.join(self.test_dir, "test_file.txt")

        # Crear el directorio de prueba si no existe
        os.makedirs(self.test_dir, exist_ok=True)

        # Crear un archivo de prueba dentro del directorio
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("Contenido de prueba para leer.\nLínea 2.")

    def tearDown(self):
        """Detener los parches y limpiar el entorno de prueba."""
        patch.stopall()
        if os.path.exists(self.test_dir):
            for root, dirs, files in os.walk(self.test_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(self.test_dir)

    def test_normalize_path(self):
        """Probar la normalización de rutas."""
        path = "ReGenesis\\capitulo1"
        normalized = executor.normalize_path(path)
        self.assertEqual(normalized, "ReGenesis/capitulo1")

    def test_is_path_potentially_dangerous_safe(self):
        """Probar que una ruta segura no se marque como peligrosa."""
        safe_path = "ReGenesis/capitulo1"
        result = executor.is_path_potentially_dangerous(safe_path, self.base_dir)
        self.assertFalse(result)

    def test_is_path_potentially_dangerous_unsafe(self):
        """Probar que una ruta peligrosa se marque como peligrosa."""
        unsafe_path = "../../outside"
        result = executor.is_path_potentially_dangerous(unsafe_path, self.base_dir)
        self.assertTrue(result)

    def test_adjust_command_paths(self):
        """Probar el ajuste de rutas en los argumentos del comando."""
        command = "tree test_dir"
        adjusted_command = executor.adjust_command_paths(command, self.base_dir)
        expected_command = f'tree "{os.path.join(self.base_dir, "test_dir")}"'
        self.assertEqual(adjusted_command, expected_command)

    @patch('executor.subprocess.run')
    def test_execute_action_valid_command(self, mock_subprocess_run):
        """Probar la ejecución de un comando válido."""
        mock_subprocess_run.return_value = MagicMock(
            stdout="Ejecución exitosa",
            stderr="",
            returncode=0
        )
        result = executor.execute_action("execute_command", "tree test_dir")
        self.assertIn("Ejecución exitosa", result)

    @patch('executor.subprocess.run')
    def test_execute_action_invalid_command(self, mock_subprocess_run):
        """Probar la ejecución de un comando inválido."""
        mock_subprocess_run.side_effect = FileNotFoundError("Comando no encontrado")
        result = executor.execute_action("execute_command", "tree ../../outside")
        self.assertIn("Error: Directorio de trabajo no encontrado o comando inválido", result)

    def test_execute_action_unrecognized_label(self):
        """Probar el manejo de etiquetas no reconocidas."""
        result = executor.execute_action("unknown_label", "contenido")
        self.assertIn("Error: Etiqueta de acción no reconocida", result)

    def test_02_read_file_relative(self):
        """Probar leer el contenido de un archivo de prueba (relativo a HISTORIAS_DIR)."""
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("Contenido de prueba para leer.\nLínea 2.")

        result = executor.execute_action("execute_command", f"Get-Content '{self.test_file}'")
        print(f"Resultado del comando: {result}")  # Agregar registro para depuración

        self.assertIn("Contenido de prueba para leer.", result)
        self.assertIn("Línea 2.", result)

    def test_03_write_file_relative(self):
        """Probar escribir en un archivo nuevo (relativo a HISTORIAS_DIR)."""
        test_write_file = os.path.join(self.test_dir, "test_write.txt")
        content_to_write = "Contenido escrito por la prueba."

        result = executor.execute_action(
            "execute_command",
            f'Set-Content -Path "{test_write_file}" -Value "{content_to_write}"'
        )
        print(f"Resultado del comando: {result}")  # Agregar registro para depuración

        with open(test_write_file, "r", encoding="utf-8") as f:
            read_content = f.read().strip()

        self.assertEqual(read_content, content_to_write, "El contenido del archivo escrito no coincide")

if __name__ == "__main__":
    unittest.main()
