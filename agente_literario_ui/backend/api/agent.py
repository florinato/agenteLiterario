import os
import re
import subprocess  # Keep import if other parts use it, otherwise remove
import sys

from fastapi import APIRouter, HTTPException
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel

import agente_literario_ui.backend.logging_manager as logging_manager
from agente_literario_ui.backend import model_manager
from agente_literario_ui.backend.executor import handle_command

# Add the parent directory (agenteLiterario) to the Python path
# This allows importing modules like executor, model_integration, etc.
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

#from agente_literario_ui.backend.executor import \
#    handle_command  # Import executor directly
# Now you can import your agent modules
#from agente_literario_ui.backend.model_integration import \
#    GeminiLLM  # Import the refactored LLM

router = APIRouter()

# --- Conversation Memory (Simple In-Memory - Needs proper session management for persistence) ---
# For now, this creates a new memory for each API instance, not ideal for long conversations.
# A better approach would involve session IDs and storing/retrieving memory per session.
# Consider using a dictionary keyed by session ID if persistence is needed later.
conversation_memory = ConversationBufferMemory()
# --- ---

class AgentCommandRequest(BaseModel):
    prompt: str
    file_path: str # Required: The path of the file being edited

class AgentCommandResponse(BaseModel):
    response: str

@router.post("/command", response_model=AgentCommandResponse)
async def run_agent_command(request: AgentCommandRequest):
    """
    Executes an agent command based on the provided prompt, managing conversation flow.
    """
    #gemini_llm = GeminiLLM()
    model_manager_instance = model_manager.ModelManager()

    # Initialize ConversationChain here, using the LLM and memory
    # Note: Using the global 'conversation_memory'. This means memory persists
    # across calls within the same API process lifetime, but not across restarts
    # or different processes. Resetting might be needed.
    # TODO: Implement proper session-based memory management.
    cleaned_command = None
    logging_manager.logging.debug("API Agent", f"run_agent_command called with command: {cleaned_command}")

    # Define the explicit prompt template
    #prompt_template = PromptTemplate(
    #    input_variables=["history", "input"],
    #    template=gemini_llm.get_system_instructions() + """

    #Historial de Conversación:
    #{history}

    #Usuario: {input}
    #Agente (responde en español):"""
    #)

    #conversation = ConversationChain(
    #    llm=gemini_llm,
    #    memory=conversation_memory, # Use the shared (but currently non-persistent) memory
    #    prompt=prompt_template, # Use the custom prompt template
    #    verbose=True  # Keep verbose for debugging
    #)

    # Imprime el prompt completo antes de enviarlo al modelo
    #logging_manager.logging.debug("System Prompt + Historial", conversation.prompt.format(history=conversation_memory.load_memory_variables({})['history'], input=request.prompt))

    # --- Main Interaction Loop ---
    current_prompt = request.prompt  # Start with the user's initial prompt
    max_iterations = 20 # Limit iterations to prevent infinite loops
    iteration = 0
    final_agent_response = None

    while iteration < max_iterations:
        iteration += 1
        # Get response from ConversationChain
        # The chain implicitly includes history and system instructions (if configured in LLM/prompt)
        #llm_response = conversation.predict(input=current_prompt)
        llm_response = model_manager_instance.get_response(current_prompt)

        # --- Process LLM Response (Search for labels anywhere) ---
        command_match = re.search(r"(?:execute_command:\s*)+([^\n]*)", llm_response, re.IGNORECASE | re.DOTALL)

        if command_match:
            command = command_match.group(1).strip()
            # Clean command (ensure it's safe and targets 'historias')
            cleaned_command = command.rstrip('`').strip()

            # Prevent potentially harmful commands (basic check)
            if cleaned_command.startswith("rm ") or cleaned_command.startswith("del "):
                logging_manager.logging.warning("Blocked potentially harmful command")
                final_agent_response = "Error: Comando potencialmente peligroso bloqueado."
                break
        
            if cleaned_command.startswith("arbol"):
                final_agent_response = model_manager_instance.get_file_tree()
                break

            #logging_manager.logging.debug("Agent Command", "Comando original: {}\nComando limpio: {}".format(command.replace('%', '%%'), cleaned_command.replace('%', '%%')))
            #command_to_execute = cleaned_command

            # Log the complete command before passing it to handle_command
            #logging_manager.logging.debug("Agent Command - Before handle_command", f"Comando completo: {command_to_execute}")

            # Execute the command
            try:
                def replace_backslashes(ruta):
                    return ruta.replace("\\", "/")

                cleaned_command_processed = cleaned_command
                if cleaned_command.startswith("leer"):
                    partes = cleaned_command.split(" ", 1)
                    if len(partes) > 1:
                        _, ruta = partes
                        ruta_procesada = replace_backslashes(ruta)
                        cleaned_command_processed = "leer " + ruta_procesada
                executor_response = handle_command(cleaned_command_processed)
                #final_agent_response = executor_response
                #executor_response = handle_command(command_to_execute)
                # Prepare the result as the next prompt for the LLM
                #current_prompt = executor_response
                # Continue the loop to feed result back to LLM
                if cleaned_command.startswith("leer"):
                    current_prompt = executor_response
                    final_agent_response = None
                else:
                    final_agent_response = executor_response
            except Exception as exec_error:
                logging_manager.log_error("Error executing command", f"Error executing command '{{command_to_execute}}': {{exec_error}}")
                final_agent_response = f"Error al ejecutar el comando: {exec_error}"
                break  # Exit loop on execution error

        # If no command or replace was found, treat the entire response as the final user message
        else:
            # Clean potential "respuesta usuario:" prefix if present, but treat the whole thing as final response
            if llm_response.startswith("respuesta usuario:"):
                final_agent_response = llm_response[len("respuesta usuario:"):].strip()
            else:
                 final_agent_response = llm_response # Use the raw response if no prefix

            logging_manager.logging.debug("API Agent", "No command/replace found, treating as final user response. ")
            # Check if the final response still contains accidental commands (log warning)
            if "execute_command:" in final_agent_response or "replace:" in final_agent_response:
                 logging_manager.logging.warning("Command/Replace potentially missed", f"Command/Replace potentially missed in final response: {final_agent_response}")

            break # Exit loop, this is the final response for this turn
            
        logging_manager.add_log(f"Usuario: {current_prompt}\nAgente: {llm_response}")

    # --- End Interaction Loop ---

    if final_agent_response is None:
         # This happens if max_iterations is reached without break
         logging_manager.logging.warning("Agent loop finished without a final response (max iterations reached?).")
         # Provide the last command output or a generic message
         if current_prompt.startswith("System Execution Result:"):
             final_agent_response = current_prompt # Return the last execution result
         else:
             final_agent_response = "Error: El agente alcanzó el límite de iteraciones sin una respuesta final."

    # Return the determined final response
    return AgentCommandResponse(response=final_agent_response)

    #except Exception as e:
    #    # Log the general error during agent command execution
    #    logging_manager.logging.error("Error executing agent command", f"Error executing agent command: {type(e).__name__} - {e}")
    #    raise HTTPException(status_code=500, detail=f"Error interno del servidor al ejecutar el comando del agente.")
#except Exception as e:
    logging_manager.logging.error("Error executing agent command", f"Error executing agent command: {type(e).__name__} - {e}", exc_info=True)
    raise
