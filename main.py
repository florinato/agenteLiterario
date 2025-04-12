# main.py
import os
import re

# Langchain imports
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate

# Local imports
from agente_literario_ui.backend import (communication, executor,
                                         logging_manager, security)
from agente_literario_ui.backend.model_integration import \
    GeminiLLM  # Importar la clase LLM directamente

# Definir la plantilla del prompt para Langchain
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()
TEMPLATE = f"{system_prompt}\nHistorial de la conversación:\n{{history}}\n\nEntrada del usuario: {{input}}\nTu respuesta (con etiqueta):"


PROMPT = PromptTemplate(input_variables=["history", "input"], template=TEMPLATE)


def main():
    # Inicializar LLM, Memoria y Cadena de Conversación
    llm = GeminiLLM()
    # Usar prefijos genéricos que funcionen para cualquier tipo de agente
    memory = ConversationBufferMemory(memory_key="history", human_prefix="Entrada", ai_prefix="Respuesta Modelo")
    conversation = ConversationChain(
        llm=llm,
        prompt=PROMPT,
        verbose=False, # Poner a True para ver el prompt completo enviado a Langchain
        memory=memory
    )

    log_file_path = os.path.abspath(logging_manager.LOG_FILE)
    print("Agente Literario con Gemini (Langchain): Iniciando sesión...") # Mensaje actualizado
    print(f"Las interacciones de depuración se guardarán en: {log_file_path}")

    # Bucle principal de interacción con el usuario
    while True:
        user_query = input("Tu consulta para el Agente Literario (o 'salir' para terminar): ") # Mensaje actualizado
        if user_query.lower() == 'salir':
            print("Finalizando sesión.")
            break

        logging_manager.log_debug("User Query", user_query)

        # Variable para pasar la entrada al modelo en cada iteración
        current_input = user_query
        is_first_iteration = True

        # Bucle de iteración autónoma para una consulta de usuario
        while True:
            # Obtener respuesta del modelo
            if is_first_iteration:
                model_response_raw = conversation.predict(input=current_input)
                #logging_manager.log_debug(f"Respuesta Modelo Raw (Iteración Inicial)", model_response_raw)
            else:
                history = memory.load_memory_variables({})['history']
                model_response_raw = conversation.predict(input=f"{user_query}\nHistorial de la conversación:\n{history}")

            #if is_first_iteration:
            #    logging_manager.log_debug(f"Respuesta Modelo Raw (Iteración Inicial)", model_response_raw)
            #else:
            #    logging_manager.log_debug(f"Respuesta Modelo Raw (Iteración Interna)", model_response_raw)

            label, content = communication.parse_message(model_response_raw)

            if not label:
                logging_manager.log_debug("Error Parseo", f"No se pudo parsear: {model_response_raw}")
                print(f"Error: Respuesta inesperada del modelo: {model_response_raw}")
                # Guardar la respuesta no parseada en memoria como respuesta de IA
                # Usamos la etiqueta 'respuesta_usuario' para que el ciclo termine y se muestre el error.
                conversation.memory.save_context({"input": current_input}, {"output": f"respuesta_usuario: Error interno - respuesta no reconocida: {model_response_raw}"})
                break # Salir del bucle interno en caso de error de parseo

            # Ejecutar si es un comando CLI o una llamada a herramienta
            # NOTE: 'tool_call' is no longer expected based on executor.py simplification,
            # but we keep the check here in case the prompt still generates it.
            # The executor will return an error for 'tool_call'.
            if label == "execute_command" or label == "tool_call":
                is_first_iteration = False # Ya no es la primera iteración

                # NOTE: Se elimina el chequeo de seguridad explícito en Python (security.is_action_dangerous).
                # La seguridad ahora depende de:
                # 1. El agente (LLM) pidiendo confirmación ANTES de generar comandos peligrosos (según el prompt).
                # 2. La herramienta 'execute_command' externa usando 'requires_approval=true' si es necesario.

                # Ejecutar la acción
                # executor.execute_action ahora maneja principalmente 'execute_command'
                output = executor.execute_action(label, content)
                logging_manager.log_debug(f"Salida Acción ({label})", output)

                # Crear respuesta del sistema etiquetada
                respuesta_sistema_etiquetada = communication.create_respuesta_sistema(output)
                logging_manager.log_debug("Respuesta Sistema Etiquetada", respuesta_sistema_etiquetada)

                # Preparar la respuesta del sistema como la *siguiente entrada* para el modelo
                current_input = respuesta_sistema_etiquetada
                # Continuar el bucle interno para el siguiente paso autónomo

            elif label == "respuesta_usuario":
                # Si el modelo dio una respuesta directa al usuario, la tarea terminó para esta consulta.
                logging_manager.log_debug("Respuesta Usuario Final", model_response_raw)
                # Extraer el contenido del mensaje
                _, content = communication.parse_message(model_response_raw)
                print(content)
                # Langchain ya guardó la respuesta final en memoria con predict
                break # Salir del bucle interno, volver a esperar input del usuario externo

            else:
                # Error de etiqueta desconocida (ya no debería ocurrir si parse_message es robusto)
                print(f"Error: Etiqueta desconocida o formato incorrecto procesado: {model_response_raw}")
                logging_manager.log_debug("Error Etiqueta Desconocida", f"Etiqueta: {label}, Contenido: {content}")
                # Guardar respuesta no reconocida y salir del bucle interno
                conversation.memory.save_context({"input": current_input}, {"output": f"respuesta_usuario: Error interno - etiqueta no reconocida: {label}"})
                break # Salir del bucle interno


if __name__ == "__main__":
    main()
